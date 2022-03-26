from collections import defaultdict
from functools import partial
import json
import itertools
from concurrent.futures import Future

def dump(*args, **kwargs):
	"""Identical to json.dump(), but produces JSOG"""
	encoded = encode(args[0])
	args = (encoded,) + args[1:]
	json.dump(*args, **kwargs)

def dumps(*args, **kwargs):
	"""Identical to json.dumps(), but produces JSOG"""
	encoded = encode(args[0])
	args = (encoded,) + args[1:]
	return json.dumps(*args, **kwargs)

def load(*args, **kwargs):
	"""Identical to json.load(), but understands JSOG. Works on plain JSON, but incurs some additional processing overhead."""
	obj = json.load(*args, **kwargs)
	return decode(obj)

def loads(*args, **kwargs):
	"""Identical to json.loads(), but understands JSOG. Works on plain JSON, but incurs some additional processing overhead."""
	obj = json.loads(*args, **kwargs)
	return decode(obj)


def encode(original):
	""""Take a JSON structure with cycles and turn it into a JSOG-encoded structure. The new structure
	will have @id on every object and duplicate references will be replaced with @ref."""

	# For every object seen so far, maps stringified id() to the object
	sofar = {}
	next_id = itertools.count()

	def doEncode(original):
		if isinstance(original, dict):
			originalId = id(original)
			previous = sofar.get(originalId, None)
			if previous is not None:
				previous_id = previous.get('@id', None)
				if previous_id is None:
					previous_id = previous["@id"] = str(next(next_id))
				return { '@ref': previous_id }

			result = sofar[originalId] = {}

			for key, value in original.items():
				result[key] = doEncode(value)

			return result

		elif isinstance(original, list):
			return [doEncode(val) for val in original]

		else:
			return original

	return doEncode(original)

def decode(encoded):
	""""Take a JSOG-encoded JSON structure and create a new structure which re-links all the references. The return value will
	not have any @id or @ref fields"""
	# This works differently from the JavaScript and Ruby versions. Python dicts are unordered, so
	# we can't be certain to see associated @ids before @refs. Instead we add hooks to `@ref` references
	# that are replaced whenever the @id is defined.

	# holds string id -> Future[object with that id]
	reference_cache = defaultdict(Future)

	def decode(encoded):
		if isinstance(encoded, dict):
			# Handle references
			if "@ref" in encoded:
				return reference_cache[encoded["@ref"]]

			# Decode object
			ret = {}

			for key, value in encoded.items():
				if key == "@id":
					future = reference_cache[value]
					if future.done():
						raise ValueError("Duplicate @id definition: " + repr(value))
					future.set_result(ret)
					continue

				ret[key] = decoded_value = decode(value)

				# Add callbacks on pending reference fields
				if isinstance(decoded_value, Future):
					decoded_value.add_done_callback(partial(_reference_resolved, obj=ret, key=key))

			return ret

		elif isinstance(encoded, list):
			ret = []

			for i, value in enumerate(encoded):
				decoded_value = decode(value)
				ret.append(decoded_value)
				if isinstance(decoded_value, Future):
					decoded_value.add_done_callback(partial(_reference_resolved, obj=ret, key=i))

			return ret
		else:
			return encoded

	ret = decode(encoded)

	# Check for unresolved references
	for ref, future in reference_cache.items():
		if not future.done():
			raise KeyError(ref)

	return ret

def _reference_resolved(future, obj, key):
	obj[key] = future.result()
