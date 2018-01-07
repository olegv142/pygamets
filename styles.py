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

default = {
	'*' : {
		'border'    : 1,
		'f_color'   : (0, 0, 150),   # fill color
		'font_face' : 'Arial',
		'font_size' : 72
	},
	'TextLabel' : {
		't_color'  : (0, 255, 0), # text color
	},
	'FrameWindow#result' : {
		'f_color'   : (0, 0, 255),   # fill color
		'b_color'   : (50, 0, 255),  # border color
	},
	'FrameWindow#activity' : {
		'f_color'   : (0, 0, 255),   # fill color
		'b_color'   : (50, 0, 255),  # border color
	},
	'PieProgressIndicator' : {
		'f_color'     : (0, 0, 255), 
		'done_color'  : (0, 255, 0),
		'todo_color'  : (100, 100, 100),
		'interval'    : 50,
		'period'      : 100,
	},
	'TextLabel#remaining' : {
		'font_size' : 64,
		't_color'   : (0, 255, 255), # text color
		'f_color'   : (0, 0, 255),   # fill color
	},
	'TextLabel#result' : {
		't_color'   : (0, 255, 0), # text color
		'f_color'   : (0, 0, 255), # fill color
	},
	'TextLabel#status' : {
		'font_size' : 32
	},
	'TextLabel#info' : {
		'font_size' : 24
	},
	'TextButton' : {
		't_color'  : (0, 255, 0),  # text color
		'tp_color' : (0, 100, 0),  # text color in pressed state
	},
	'PulseTextButton' : {
		't1_color'  : (255, 255, 255),
		't0_color'  : (0, 0, 255),
		'tp_color'  : (100, 0, 100),  # text color in pressed state
		'interval'  : 50,
		'period'    : 100,
		'decay'     : 30,
	},
	'XButton' : {
		'x_color'  : (0, 255, 0),  # X mark color
		'xp_color' : (0, 100, 0),  # X mark color in pressed state
		'x_width'  : 4,            # X mark line width
		'x_margin' : .3            # X mark margin relative to the button width
	},
	'BatteryIndicator' : {
		'roundness'    : .15,
		'tip_height'   : .07,
		'tip_diameter' : .5,
		'alert_charge' : .1,
		'charge_color' : (0, 255, 0),
		'alert_color'  : (255, 0, 0),
		'batt_color'   : (100, 100, 100),
		'font_size'    : 24,
		't_color'      : (255, 255, 255)
	},
	'Demo' : {
		'screen_w'      : 480,
		'screen_h'      : 320,
		'max_fps'       : 50,
		'status_panel_h': 50,
		'info_panel_h'  : 40,
		'start_margin'  : 40,
		'active_margin' : 25,
		'result_margin' : 25,
		'progress_sz'   : .7,
		'ini_progress'  : .07,
		'fin_progress'  : .07,
		'batt_width'    : 80,
		'batt_margin'   : 10,
		'batt_charge'   : .8,
		'close_btn_sz'  : 50,
		'status_colors' : {
			0 : (0, 0, 0), 
			1 : (0, 255, 255), # initializing
			2 : (0, 255, 0),   # ready
			3 : (255, 255, 0), # busy
			8 : (255, 0, 0),   # failed
		},
		'info_colors' : {
			0 : (0, 255, 0),   # normal
			1 : (255, 255, 0), # warning
			2 : (255, 0, 0),   # error
		},
	}
}
