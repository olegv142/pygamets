"""
Localization support
"""

import localization

def localize(text):
	try:
		return localization.default[text]
	except KeyError:
		return text
