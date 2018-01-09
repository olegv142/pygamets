"""
GUI styles definitions.
The default should be the dictionary of dictionaries with key -> value mapping
The top level dictionary keys may have the following formats:
	*           - apply to all instances
	*[name]     - apply to all instances with specific name
	*#tag       - apply to all instances with specific tag
	Class       - apply to all instances with specific class
	Class[name] - apply to all instances with given class, name pair
	Class#tag   - apply to all instances with given class, tag pair
	Parent.Class, Parent.Parent.Class, ... - apply to the all instances with specific class chain in the elements hierarchy
	Parent.Class[name], Parent.Parent.Class[name], ... - apply to the all instances with given name and with specific class chain in the elements hierarchy
	Parent.Class#tag, Parent.Parent.Class#tag, ...     - apply to the all instances with given tag  and with specific class chain in the elements hierarchy
See style.py for lookup algorithm details.
"""

import progress

default = {
	# example configuration applied to all style instances
	'*' : {
		'border'    : 1,
		'f_color'   : (0, 0, 150), # fill colour
		'font_face' : 'Arial',
		'font_size' : 72
	},
}
