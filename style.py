"""
Cascading style sheets for GUI attributes
"""

import styles

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

	def bind_owner(self, owner):
		"""
		Set reference to the owner object - typically the view instance.
		We use owner owner class and parent link to lookup attribute defaults.
		"""
		self._owner = owner

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
		v = Style._lookup_default(self._owner, self._attrs.get('name', None), key)
		# store lookup result to speed up subsequent lookups of the same key
		self._attrs[key] = v
		return v

	@staticmethod
	def _lookup_default(obj, name, key, path = ''):
		"""Lookup default value for the given object / key pair"""
		assert obj is not None
		# Lookup the most specific path first
		if path:
			try:
				parent = obj.parent
			except AttributeError:
				parent = None
			if parent:
				v = Style._lookup_default(parent, name, key, type(parent).__name__ + '.' + path)
				if v is not None:
					return v
		else:
			v = Style._lookup_default(obj, name, key, type(obj).__name__)
			if v is not None:
				return v
			path = '*'
		if name is not None:
			try:
				return styles.default[path+'['+name+']'][key]
			except KeyError:
				pass
		try:
			return styles.default[path][key]
		except KeyError:
			pass
		return None

def bind(seed, obj):
	"""Bind style object to the owner creating it if necessary. Returns bound style object."""
	if seed is None:
		seed = Style()
	seed.bind_owner(obj)
	return seed
