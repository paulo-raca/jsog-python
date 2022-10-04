import json
import itertools

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
		def encodeObject(original):
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

		def encodeArray(original):
			return [doEncode(val) for val in original]

		if isinstance(original, list):
			return encodeArray(original)
		elif isinstance(original, dict):
			return encodeObject(original)
		else:
			return original

	return doEncode(original)

def decode(encoded):
	""""Take a JSOG-encoded JSON structure and create a new structure which re-links all the references. The return value will
	not have any @id or @ref fields"""
	# This works differently from the JavaScript and Ruby versions. Python dicts are unordered, so
	# we can't be certain to see associated @ids before @refs. Instead we will make two passes,
	# the first builds the object graph and tracks @ids; the second actually replaces @ref references
	# with the associated object.

	# holds string id -> copied object with that id. in the first pass, it will leave @refs alone.
	found = {}

	def firstPassDecode(encoded):
		def firstPassDecodeObject(encoded):
			if '@ref' in encoded:
				# first pass leaves these alone
				return encoded

			result = {}

			if '@id' in encoded:
				found[encoded['@id']] = result

			for key, value in encoded.items():
				if key != '@id':
					result[key] = firstPassDecode(value)

			return result

		def firstPassDecodeArray(encoded):
			return [firstPassDecode(value) for value in encoded]

		if isinstance(encoded, list):
			return firstPassDecodeArray(encoded)
		elif isinstance(encoded, dict):
			return firstPassDecodeObject(encoded)
		else:
			return encoded

	def deref(withRefs):
		if isinstance(withRefs, dict):
			for key, value in withRefs.items():
				if isinstance(value, dict) and '@ref' in value:
					withRefs[key] = found[value['@ref']]
				else:
					deref(value)
		elif isinstance(withRefs, list):
			for i, value in enumerate(withRefs):
				if isinstance(value, dict) and '@ref' in value:
					withRefs[i] = found[value['@ref']]
				else:
					deref(value)

	firstPass = firstPassDecode(encoded)
	deref(firstPass)
	return firstPass
