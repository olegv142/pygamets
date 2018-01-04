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
		self._owner = owner

	def __getattribute__(self, key):
		try:
			return object.__getattribute__(self, key)
		except AttributeError:
			pass
		try:
			return self._attrs[key]
		except KeyError:
			pass
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
			if obj.parent:
				v = Style._lookup_default(obj.parent, name, key, type(obj.parent).__name__ + '.' + path)
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
