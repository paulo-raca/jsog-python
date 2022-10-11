from jsog3 import jsog
import unittest

class TestJSOG(unittest.TestCase):

	def test_encode_reference(self):
		inner = { "foo": "bar" }
		outer = { "inner1": inner, "inner2": inner }
		encoded = jsog.encode(outer)

		inner1 = encoded['inner1']
		inner2 = encoded['inner2']

		# one has @id, one has @ref
		self.assertNotEqual('@id' in inner1, '@id' in inner2)
		self.assertNotEqual('@ref' in inner1, '@ref' in inner2)

		if '@id' in inner1:
			self.assertEqual('0', inner1['@id'])
			self.assertEqual('0', inner2['@ref'])
		else:
			self.assertEqual('0', inner2['@id'])
			self.assertEqual('0', inner1['@ref'])

	def test_decode_reference(self):
		JSOGIFIED = '{"@id":"1","foo":"foo","inner1":{"@id":"2","bar":"bar"},"inner2":{"@ref":"2"}}'
		parsed = jsog.loads(JSOGIFIED)

		inner1 = parsed['inner1']
		inner2 = parsed['inner2']
		self.assertTrue(inner1 is inner2)

	def test_encode_circular(self):
		thing = {}
		thing['me'] = thing
		thing['list'] = [thing]

		encoded = jsog.encode(thing)

		self.assertEqual(encoded, {
			'@id': '0',
			'me': { '@ref': '0' },
			'list': [ { '@ref': '0' } ],
		})

	def test_decode_circular(self):
		thing = {}
		thing['me'] = thing
		thing['list'] = [thing]

		encoded = jsog.encode(thing)
		back = jsog.decode(encoded)

		self.assertFalse('@id' in back)
		self.assertTrue(back['me'] is back)
		self.assertTrue(back['list'][0] is back)

	def test_encode_null(self):
		encoded = jsog.encode(None)
		self.assertEqual(encoded, None)

	def test_decode_null(self):
		decoded = jsog.decode(None)
		self.assertEqual(decoded, None)

	def test_decode_plain_json(self):
		json = { "foo": "bar" }
		decoded = jsog.decode(json)
		self.assertEqual(json, decoded)

	def test_decode_list_reference(self):
		JSOGIFIED = '{"@id":"1","foo":"foo","inner1":{"@id":"2","bar":"bar"},"inner2":[{"@ref":"2"}]}'
		parsed = jsog.loads(JSOGIFIED)

		inner1 = parsed['inner1']
		inner2 = parsed['inner2'][0]
		self.assertTrue(inner1 is inner2)

	def test_decode_missing_id(self):
		with self.assertRaises(KeyError):
			json = { "foo": { "@ref": "1" }, "bar": { "@ref": "1" } }
			jsog.decode(json)


	def test_decode_duplicate_id(self):
		with self.assertRaises(ValueError):
			json = { "foo": { "@id": "1" }, "bar": { "@id": "1" } }
			jsog.decode(json)

	def test_decode_root_ref(self):
		with self.assertRaises(KeyError):
			json = { "@ref": "0" }
			jsog.decode(json)


if __name__ == '__main__':
	unittest.main()
