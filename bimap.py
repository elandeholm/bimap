from collections import OrderedDict

"""
	Bimap provides a method to bijectively map distinct immutable items
	to ordinals (natural numbers). The mapping is constructed as new items
	are registered. There is no way to unmap a previously registered item.

	A typical client could be a string interner in a compiler or interpreter.



	Bimap supports the following protocols, mostly by delegation to the underlying
	OrderedDict.

		bool()
			False if empty, True otherwise.

		repr()
			eval()-roundtrip safe.

		__getitem__()
			Provides Bimap[item] -> ordinal.

		comparison (__eq__ and __ne__)

		len()

		iter()
			''for o in self'' iterates over the set of currently mapped items in order
			 of registration.



	In addition to these:

		__init__(*arg)
			Initializes a mapping from a list of item arguments. Argument order is respected,
			so that the 0:th item is taken from the first argument etc.

		register(item) -> ordinal
			Provides an idempotent method of adding (or looking up) items to the map.

		ordinal(item) -> ordinal
			Gives the ordinal of a registered item, or None.

		item(n) -> item
		nth(n) -> item
			Gives the item mapped to the n:th ordinal.

		ordinals()
			Returns the underlying OrderedDict. Can be used to iterate over the mapping ordinals:

			for n in bm.ordinals():
				pass

		enumerate()
			Enumerate the item, ordinal pairs in order of registration. This is simply a
			delegation to the underlying OrderedDict's .items()

			for item, ordinal in bm.items():
				pass

		range()
			Returns the range of ordinals mapped.

		domain()
			Constructs a set of the mapped items (thus losing order).
"""

__license__ = "poetic"

class Bimap():
	def __init__(self, *args):
		self._classname = type(self).__name__
		self.item2ord = OrderedDict()
		self.ord2item = OrderedDict()

		for item in args:
			self.register(item)

	def _internal(self):
		return self._classname, self.item2ord, self.ord2item

	def __bool__(self):
		return bool(self.item2ord)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.item2ord == other.item2ord
		return NotImplemented

	def __ne__(self, other):
		result = self.__eq__(other)
		if result is NotImplemented:
			return result
		return not result

	def __repr__(self):
		args = ', '.join([ repr(x) for x in self ])
		return '{}({})'.format(self._classname, args)

	def __len__(self):
		return len(self.item2ord)

	def __iter__(self):
		return iter(self.item2ord)

	def __getitem__(self, item):
		try:
			return self.item2ord[item]
		except KeyError:
			return None

	def register(self, item):
		if item is None:
			raise ValueError(self._classname + ' cannot register "None"')
		try:
			return self.item2ord[item]
		except KeyError:
			ordinal = len(self)
			self.item2ord[item] = ordinal
			self.ord2item[ordinal] = item
			return ordinal

	def ordinal(self, item):
		return self[item]

	def item(self, ordinal):
		try:
			return self.ord2item[ordinal]
		except KeyError:
			return None

	def nth(self, ordinal): # just an alias for .item()
		return self.item(ordinal)

	def ordinals(self):
		return self.ord2item.keys()

	def enumerate(self):
		return self.item2ord.items()

	def range(self):
		return set(self)

	def domain(self):
		return range(len(self))

if __name__ == '__main__':
	bm = Bimap()

	test_items = [ 'xyzzy', 'plugh', 'foo', 'bar', 'ack!' ]

	# Verify that None can't be mapped

	try:
		bm.register(None)
	except ValueError:
		pass
	else:
		raise AssertionError('Bimap should not accept register(None)')

	# Test bool() of empty Bimap

	assert bool(bm) == False

	# Add five distinct strings

	for item in test_items:
		bm.register(item)

	# Test bool() again

	assert bool(bm) == True

	# Test comparison

	bm2 = Bimap()

	assert bm != bm2

	# Add the five strings out of order

	for item in reversed(test_items):
		bm2.register(item)

	# Test comparison again
	# Same items, different order

	assert bm != bm2

	# Test .__init__() arguments (and comparison)

	bm2 = Bimap(*test_items)

	assert bm == bm2

	bm2 = Bimap('plugh', 'xyzzy', 'foo', 'bar', 'ack!')

	assert bm != bm2

	# Test repr()

	assert '{}'.format(bm) == "Bimap('xyzzy', 'plugh', 'foo', 'bar', 'ack!')"

	# Test _internal()

	try:
		assert repr(bm._internal()) == "('Bimap', OrderedDict([('xyzzy', 0), ('plugh', 1), ('foo', 2), ('bar', 3), ('ack!', 4)]), OrderedDict([(0, 'xyzzy'), (1, 'plugh'), (2, 'foo'), (3, 'bar'), (4, 'ack!')]))"
	except AssertionError:
		print(repr(bm._internal()))
		raise

	# Test idempotency

	assert bm.register('plugh') == 1
	assert bm.register('xyzzy') == 0
	assert bm.register('plugh') == 1
	assert bm.register('ack!')  == 4
	assert bm.register('plugh') == 1

	# Test .nth()

	assert bm.nth(2) == 'foo'
	assert bm.nth(4) == 'ack!'
	assert bm.nth(0) == 'xyzzy'

	# Test .__getitem__(), verify that an unmapped item returns None

	assert bm['ack!']  == 4
	assert bm['xyzzy'] == 0
	assert bm['wat!']  == None

	# Test .enumerate(), verifying the bijectivity of the mapping

	for item, ordinal in bm.enumerate():
		assert bm.nth(ordinal) == item
		assert bm.ordinal(item) == ordinal

	# Test .__iter__() via ''for''

	l = [ ]
	for x in bm:
		l.append(x)

	assert l == test_items

	# Test .__iter__() via list()

	assert list(bm) == test_items

	# Test len()

	assert len(bm) == 5

	# Test .domain()

	assert bm.domain() == range(5)

	# Test .range()

	assert bm.range() == set(test_items)

	# Test .ordinals()

	assert list(bm.ordinals()) == [ 0, 1, 2, 3, 4 ]

	# Test .enumerate()

	assert list(bm.enumerate()) == [ ('xyzzy', 0), ('plugh', 1), ('foo', 2), ('bar', 3), ('ack!', 4) ]

	# Test somewhat involved eval(repr)-roundtrip

	bm.register(( 1, 2 ))
	bm.register(b'bytes')
	bm.register(True)
	bm.register(frozenset((1, 2, 3)))
	bm.register(False)
	bm.register(tuple([ (str(k), str(v)) for k, v in globals().items() ]))
	assert bm == eval(repr(bm))

	print('All tests completed OK!')
