from collections import OrderedDict

"""
	Bimap provides a bi-directional mapping from distinct immutable objects
	to ordinals (natural numbers)

	It can be used as a simple order preserving container, eg. in a string interner



	Bimap supports the following protocols:

		bool()
			False if empty, True otherwise.

		repr()
			eval()-roundtrip safe.

		__getitem__()
			Provides Bimap[obj] -> ordinal.

		comparison (__eq__ and __ne__)

		len()

		iter()
			''for o in self'' iterates over the mapped objects in order of registration.



	In addition to these:

		__init__(*arg)
			Initializes a mapping from a list of object arguments. Argument order is respected,
			so that the 0:th object is taken from the first argument etc.

		register(obj) -> ordinal
			Provides an idempotent way of adding objects after initialization.

		ordinal(obj) -> ordinal
			Gives the ordinal of a registered object, or None.

		nth(n) -> object
			Gives the object associated with the n:th ordinal.

		ordinals()
			Returns the underlying OrderedDict association from ordinals to objects.
			Can be used as an iterator over the mapping ordinals:

			for n in bm.ordinals():
				pass

		items()
			Returns the items() ([ ( obj1, 0), (obj2, 1), ... ]) of the underlying OrderedDict.
			Can be used as an iterator over object, ordinal pairs.

			for object, ordinal in bm.items():
				pass

		range()
			Returns the range of ordinals mapped.

		domain()
			Constructs a set of the mapped objects (thus losing order).

		bimap(x)
			Returns the ordinal of the object x, or failing that,
			the x:th object, or failing that, None.
			(warning, esoteric)

"""

__license__ = "poetic"

class Bimap():
	def __init__(self, *args):
		self._classname = type(self).__name__
		self.obj2ord = OrderedDict()
		self.ord2obj = OrderedDict()

		for obj in args:
			self.register(obj)

	def _internal(self):
		return self._classname, self.obj2ord, self.ord2obj

	def __bool__(self):
		return bool(self.obj2ord)

	def __eq__(self, other):
		if isinstance(other, self.__class__):
			return self.obj2ord == other.obj2ord
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
		return len(self.obj2ord)

	def __iter__(self):
		return iter(self.obj2ord)

	def __getitem__(self, obj):
		try:
			return self.obj2ord[obj]
		except KeyError:
			return None

	def register(self, obj):
		if obj is None:
			raise ValueError(self._classname + ' cannot register "None"')
		try:
			return self.obj2ord[obj]
		except KeyError:
			ordinal = len(self)
			self.obj2ord[obj] = ordinal
			self.ord2obj[ordinal] = obj
			return ordinal

	def ordinal(self, obj):
		return self[obj]

	def nth(self, ordinal):
		try:
			return self.ord2obj[ordinal]
		except KeyError:
			return None

	def ordinals(self):
		return self.ord2obj

	def items(self):
		return self.obj2ord.items()

	def range(self):
		return range(len(self))

	def domain(self):
		return set(self)

	def bimap(self, x):
		y = self[x]
		if y is not None:
			return y
		else:
			return self.nth(x)

if __name__ == '__main__':
	bm = Bimap()

	test_objects = [ 'xyzzy', 'plugh', 'foo', 'bar', 'ack!' ]

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

	for obj in test_objects:
		bm.register(obj)

	# Test bool() again

	assert bool(bm) == True

	# Test comparison

	bm2 = Bimap()

	assert bm != bm2

	# Add the five strings out of order

	for obj in reversed(test_objects):
		bm2.register(obj)

	# Test comparison again
	# Same objects, different order

	assert bm != bm2

	# Test .__init__() arguments (and comparison)

	bm2 = Bimap(*test_objects)

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
	assert bm.register('plugh') == 1
	assert bm.register('plugh') == 1

	# Test .nth()

	assert bm.nth(2) == 'foo'
	assert bm.nth(4) == 'ack!'
	assert bm.nth(0) == 'xyzzy'

	# Test .__getitem__(), make sure nonexistant values map to "None"

	assert bm['ack!'] == 4
	assert bm['xyzzy'] == 0
	assert bm['wat!'] == None

	# Test 1-to-1, .items(), .ordinal(), .nth()

	for obj, ordinal in bm.items():
		assert bm.nth(ordinal) == obj
		assert bm.ordinal(obj) == ordinal

	# Test .__iter__()

	l = [ ]
	for x in bm:
		l.append(x)

	assert l == test_objects

	# Test list() (via .__iter__)

	assert list(bm) == test_objects

	# Test len()

	assert len(bm) == 5

	# Test .range()

	assert bm.range() == range(5)

	# Test .ordinals()

	assert list(bm.ordinals()) == [ 0, 1, 2, 3, 4 ]

	# Test .objs()

	assert list(bm.items()) == [ ('xyzzy', 0), ('plugh', 1), ('foo', 2), ('bar', 3), ('ack!', 4) ]

	# Test .bimap()

	assert bm.bimap('ack!') == 4
	assert bm.bimap(1) == 'plugh'
	assert bm.bimap(None) == None

	# Test .domain()

	assert bm.domain() == set(test_objects)

	# Test somewhat involved eval(repr)-roundtrip

	bm.register(( 1, 2 ))
	bm.register(b'bytes')
	bm.register(True)
	bm.register(frozenset((1, 2, 3)))
	bm.register(False)
	bm.register(tuple([ (str(k), str(v)) for k, v in globals().items() ]))
	assert bm == eval(repr(bm))

	print('All tests completed OK!')
