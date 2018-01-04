"""
GUI styles definitions.
The default should be the dictionary of dictionaries with key -> value mapping
The top level dictionary keys may have the following formats:
	*           - apply to all instances
	*[name]     - apply to all instances with specific name
	Class       - apply to all instances with specific class
	Class[name] - apply to all instances with given class, name pair
	Parent.Class, Parent.Parent.Class, ... - apply to the all instances with specific class chain in the elements hierarchy
	Parent.Class[name], Parent.Parent.Class[name], ... - apply to the all instances with given name and with specific class chain in the elements hierarchy
See style.py for lookup algorithm details.
"""

default = {
	'*' : {
		'border' : 2,
		't_color' : (0, 0, 0),  # text color
		'font_face' : 'Arial',
		'font_size' : 72
	},
	'RectButton' : {
		'f_color' : (0, 255, 0), # fill color
		'p_color' : (0, 100, 0), # pressed color
		'b_color' : (255, 0, 0), # border color
	},
	'TextButton' : {
		't_color'  : (0, 255, 0),  # text color
		'tp_color' : (0, 100, 0),  # text color in pressed state
		'font_size' : 32
	},
	'TextButton[Ok]' : {
		't_color'  : (255, 255, 0),  # text color
		'tp_color' : (100, 100, 0),  # text color in pressed state
		'font_size' : 32
	},
	'PulseTextButton' : {
		't1_color'  : (0, 255, 0),
		't0_color'  : (0, 0, 255),
		'tp_color'  : (0, 100, 0),  # text color in pressed state
		'font_size' : 32,
		'interval'  : 50,
		'period'    : 100,
		'decay'     : 30,
	},
	'XButton' : {
		'x_color'  : (0, 255, 0),  # X mark color
		'xp_color' : (0, 100, 0),  # X mark color in pressed state
		'x_width'  : 4,            # X mark line width
		'x_margin' : .2            # X mark margin relative to the button width
	},
}
