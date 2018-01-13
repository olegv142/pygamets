"""
Cascading style sheets for GUI attributes
"""

import styles

_styles_map = styles.default

def set_styles_map(m):
	"""Setup global styles map"""
	global _styles_map
	_styles_map = m

class Style(object):
	"""
	The style object serves 2 purposes:
	- it allows for setting any number of arbitrary named attributes in constructor
	  and serves as container for passing them to the GUI element constructor
	- it supports getting attributes that was not set explicitly by means of
	  searching them in the global CSS-like table (styles.py)
	"""
	def __init__(self, *args, **kwargs):
		self._attrs = dict(*args, **kwargs)
		self._owner = None
		self._required = set()

	def bind_owner(self, owner):
		"""
		Set reference to the owner object - typically the view instance.
		We use owner owner class and parent link to lookup attribute defaults.
		"""
		assert self._owner is None
		assert owner is not None
		self._owner = owner

	def copy(self, *args, **kwargs):
		"""Create clone of the style with owner detached"""
		s = Style()
		s._attrs = self._attrs.copy()
		s._attrs.update(*args, **kwargs)
		return s

	def require(self, attrs):
		"""
		Set attribute names that must be resolved in global registry to non None values
		unless specified explicitly in constructor.
		"""
		self._required.update(attrs)

	def __str__(self):
		return str(self._attrs)

	def __repr__(self):
		return 'Style(' + repr(self._owner) + ',' + repr(self._attrs) + ')'

	def __getattribute__(self, key):
		"""The method called on attribute resolution"""
		try:
			# resolve plain attributes like _attrs, _owner
			return object.__getattribute__(self, key)
		except AttributeError:
			pass
		try:
			# lookup at attributes dictionary
			return self._attrs[key]
		except KeyError:
			pass
		# lookup default values in global registry
		v = Style._lookup_default(self._owner, self._attrs.get('name', None), self._attrs.get('tag', None), key)
		if v is None and key in self._required:
			raise RuntimeError('can`t find required style attribute %s for %s' % (key, self._owner))
		# store lookup result to speed up subsequent lookups of the same key
		self._attrs[key] = v
		return v

	@staticmethod
	def _lookup_default(obj, name, tag, key, path = ''):
		"""Lookup default value for the given object / key pair"""
		assert obj is not None
		# Lookup the most specific path first
		if path:
			try:
				parent = obj.parent
			except AttributeError:
				parent = None
			if parent:
				v = Style._lookup_default(parent, name, tag, key, type(parent).__name__ + '.' + path)
				if v is not None:
					return v
		else:
			v = Style._lookup_default(obj, name, tag, key, type(obj).__name__)
			if v is not None:
				return v
			path = '*'
		if name is not None:
			try:
				return _styles_map[path+'['+name+']'][key]
			except KeyError:
				pass
		if tag is not None:
			try:
				return _styles_map[path+'#'+tag][key]
			except KeyError:
				pass
		try:
			return _styles_map[path][key]
		except KeyError:
			pass
		return None

def bind(obj, seed = None):
	"""Bind style object to the owner creating it if necessary. Returns bound style object."""
	if seed is None:
		seed = Style()
	seed.bind_owner(obj)
	try:
		seed.require(obj._required_attrs)
	except:
		pass
	return seed
