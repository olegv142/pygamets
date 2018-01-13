"""
Localization support
"""

import localization

_str_map = localization.default

def set_str_map(m):
	"""Setup strings map"""
	global _str_map
	_str_map = m

def localize(text):
	"""
	Lookup text in the strings map. Returns either localized text found in the map
	or the original one if the localized version is not found.
	"""
	try:
		return _str_map[text]
	except KeyError:
		return text
