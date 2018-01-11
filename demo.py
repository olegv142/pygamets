#!/usr/bin/python

"""
Generic measuring device GUI example
"""

import env
import app, gui, utils, button, label, battery, progress, style, localize
import pygame, sys, os, time, threading, functools
from log_view import LogView
from frame import Frame
from style import Style

import logging
logger = logging.getLogger('demo')
logger.setLevel(logging.DEBUG)

sys.path.append('config')
import demo_styles, demo_localization
style.styles = demo_styles
localize.localization = demo_localization

# Status values
sta_none         = 0
sta_initializing = 1
sta_ready        = 2
sta_busy         = 3
sta_failed       = 8

sta_names = {
	sta_none         : 'None',
	sta_initializing : 'Initializing',
	sta_ready        : 'Ready',
	sta_busy         : 'Measuring',
	sta_failed       : 'Failed',
}

# Info levels
inf_normal  = 0
inf_warning = 1
inf_error   = 2

class Demo(object):
	"""Demo application with separate thread"""
	_required_attrs = (
		'screen_w', 'screen_h', 'max_fps',
		'status_panel_h', 'info_panel_h', 'close_btn_sz',
		'start_margin', 'active_margin', 'result_margin',
		'progress_sz', 'ini_progress', 'fin_progress',
		'batt_width', 'batt_margin', 'batt_charge',
		'status_colors', 'info_colors',
		'progress_indicator'
	)

	def __init__(self):
		# Using s_ prefix for screen elements
		self.screen       = gui.Screen() # Screen
		self.s_background = None # Background screen
		self.s_battery    = None # Battery indicator
		self.s_status     = None # Status string at the top of the screen
		self.s_info       = None # Info string at the bottom of the screen
		self.s_start      = None # Start button
		self.s_action     = None # Action screen
		self.s_progress   = None # Progress indicator
		self.s_remaining  = None # Remaining time
		self.s_result     = None # Result screen
		self.worker       = threading.Thread(target = self.x_worker)
		self.worker.daemon= True
		self.start_time   = None
		self.start_evt    = threading.Event()
		self.stop_evt     = threading.Event()
		self.status       = sta_none
		self.style        = style.bind(self)

	def show_main_screen(self):
		"""
		Show main screen with 2 information panels, battery indicator and start button
		"""
		W, H = self.style.screen_w, self.style.screen_h
		status_panel_h = self.style.status_panel_h
		info_panel_h   = self.style.info_panel_h

		self.screen.init_mode((W, H))
		self.s_background = gui.Window(0, 0, Frame(W, H, Style(tag='background')))
		iW, iH = self.s_background.int_size()

		close_btn = button.XButton(status_panel_h)
		close_btn.clicked.connect(self.quit)
		utils.add_top_left(self.s_background, close_btn)

		log_btn = button.TextButton(status_panel_h, status_panel_h, Style(name='i'))
		log_btn.clicked.connect(self.show_log)
		utils.add_top_right(self.s_background, log_btn)

		self.s_battery = battery.BatteryIndicator(self.style.batt_width, status_panel_h - 2 * self.style.batt_margin)
		self.s_battery.set_charge(self.style.batt_charge)
		utils.add_top_right(self.s_background, self.s_battery, self.style.batt_margin, self.style.batt_margin, next_to = log_btn)

		self.s_status = label.TextLabel(self.s_battery.left() - close_btn.right(), status_panel_h, Style(tag='status'))
		utils.add_top_left(self.s_background, self.s_status, next_to = close_btn)

		self.s_info = label.TextLabel(iW, info_panel_h, Style(tag='info'))
		utils.add_left_bottom(self.s_background, self.s_info)

		start_margin = self.style.start_margin
		btn = button.PulseTextButton(iW, iH - status_panel_h - info_panel_h - 2*start_margin, Style(name='START'))
		btn.clicked.connect(self.start_activity)
		utils.add_left_bottom(self.s_background, btn, ymargin = start_margin, next_to = self.s_info)

		log_view = LogView(W, H)
		self.s_log_window = gui.Window(0, 0, log_view)
		logger.addHandler(log_view)
		self.screen.show(self.s_background)

		timer = app.Timer(self.idle_timer, 1000, True)
		app.instance.add_timer(timer)

	def show_log(self):
		"""Show log window"""
		logger.error('just test error message, the long string will be truncated truncated truncated truncated truncated truncated truncated truncated')
		self.screen.show(self.s_log_window)

	def idle_timer(self):
		logger.debug('idle_timer')

	def show_activity_screen(self):
		"""Show activity screen with progress indicator"""
		W, H, margin = self.style.screen_w, self.style.screen_h, self.style.active_margin
		self.s_action = gui.Window(
				margin, self.style.status_panel_h,
				Frame(
					W - 2 * margin, H - self.style.status_panel_h - self.style.info_panel_h,
					Style(tag='activity')
				)
			)
		w, h = self.s_action.int_size()
		btn = button.XButton(self.style.close_btn_sz)
		btn.clicked.connect(self.cancel_activity)
		utils.add_top_right(self.s_action, btn)
		progress_sz = int(h * self.style.progress_sz)
		progress_margin = (h - progress_sz) / 2
		self.s_progress = self.style.progress_indicator(progress_sz)
		utils.add_top_left(self.s_action, self.s_progress, xmargin = progress_margin, ymargin = progress_margin)
		self.s_remaining = label.TextLabel(w - progress_margin - progress_sz - self.style.close_btn_sz, h, Style(tag='remaining'))
		utils.add_top_left(self.s_action, self.s_remaining, next_to = self.s_progress)
		self.screen.show(self.s_action)

	def x_show_activity_screen(self):
		"""Show activity screen from worker thread"""
		app.instance.add_job(self.show_activity_screen)
		
	def show_progress(self, val, rotating, secs_left = None):
		"""Show progress on activity screen"""
		logger.debug('show_progress: %.2f, rotating=%s, secs_left=%s', val, rotating, secs_left)
		self.s_progress.set_progress(val, rotating)
		if secs_left is not None:
			self.s_remaining.set_text(str(secs_left))
		else:
			self.s_remaining.set_text(None)

	def x_show_progress(self, val, rotating, secs_left = None):
		"""Show progress from worker thread"""
		app.instance.add_job(functools.partial(self.show_progress, val, rotating, secs_left))

	def close_activity_screen(self):
		"""Close activity screen"""
		self.s_progress = None
		self.s_action.close()

	def x_close_activity_screen(self):
		"""Close activity screen from worker thread"""
		app.instance.add_job(self.close_activity_screen)

	def show_result_screen(self):
		"""Show results screen"""
		W, H, margin = self.style.screen_w, self.style.screen_h, self.style.result_margin
		s = gui.Window(
				margin, self.style.status_panel_h,
				Frame(
					W - 2 * margin, H - self.style.status_panel_h - self.style.info_panel_h,
					Style(tag='result')
				)
			)
		w, h = self.s_action.int_size()
		btn = button.XButton(self.style.close_btn_sz)
		btn.clicked.connect(s.close)
		utils.add_top_right(s, btn)
		txt = label.TextLabel(w, h, Style(tag='result', f_color=None))
		txt.set_text('Life is good')
		utils.add_top_left(s, txt)
		self.screen.show(s)

	def x_show_result_screen(self):
		"""Show results screen from worker thread"""
		app.instance.add_job(self.show_result_screen)

	def start_activity(self):
		"""Start button handler"""
		logger.info('starting')
		self.start_evt.set()

	def cancel_activity(self):
		"""Activity screen close button handler"""
		logger.warning('cancelling')
		self.stop_evt.set()

	def set_status(self, sta):
		"""Set new status and update status panel accordingly"""
		logger.debug('set_status: %s -> %s', sta_names[self.status], sta_names[sta])
		self.status = sta
		self.s_status.set_text(sta_names[sta], self.style.status_colors[sta])

	def x_set_status(self, sta):
		"""Set new status from worker thread"""
		app.instance.add_job(functools.partial(self.set_status, sta))

	def show_info(self, text, lvl):
		"""Show info on bottom panel"""
		if lvl == inf_normal:
			logger.info(text)
		elif lvl == inf_warning:
			logger.warning(text)
		elif lvl == inf_error:
			logger.error(text)
		self.s_info.set_text(text, self.style.info_colors[lvl])

	def x_show_info(self, text, lvl):
		"""Show info from worker thread"""
		app.instance.add_job(functools.partial(self.show_info, text, lvl))

	def x_initialize(self):
		"""Experiment initialize"""
		time.sleep(1)

	def x_wait_start(self):
		"""Wait for start request"""
		self.start_evt.wait()
		self.start_evt.clear()
		self.stop_evt.clear()

	def x_prepare(self):
		"""Experiment prepare, returns expected duration"""
		time.sleep(2)
		return 8.

	def x_run(self):
		"""Run experimented, returns True if completed"""
		time.sleep(.1)
		return time.time() > self.start_time + 8.

	def x_complete(self):
		"""Complete experiment / process results"""
		time.sleep(2)

	def x_worker(self):
		"""
		Worker thread running experiments.
		It uses special asynchronous mechanisms - events and jobs for
		communicating with GUI event loop.
		"""
		x_style = style.bind(self)

		self.x_set_status(sta_initializing)
		self.x_show_info('connecting to device', inf_normal)
		self.x_initialize()
		self.x_set_status(sta_ready)
		self.x_show_info('connected to device', inf_normal)

		while True:
			self.x_wait_start()

			self.x_set_status(sta_busy)
			self.x_show_info('measurement starting', inf_normal)
			self.x_show_activity_screen()

			ini_progress, fin_progress = x_style.ini_progress, x_style.fin_progress
			progress = ini_progress
			self.x_show_progress(progress, True)

			xtime = self.x_prepare()
			self.x_show_info('measuring stuff', inf_normal)
			self.start_time = time.time()
			cancelled = False

			while True:
				if self.stop_evt.is_set():
					cancelled = True
					break
				if self.x_run():
					break
				elapsed = time.time() - self.start_time
				secs_left = int(xtime - elapsed)
				progress = ini_progress + (1 - ini_progress - fin_progress) * elapsed / xtime
				self.x_show_progress(progress, False, secs_left if secs_left > 0 else None)

			if not cancelled:
				self.x_show_progress(progress, True)
				self.x_show_info('processing results', inf_normal)
				self.x_complete()

			self.x_close_activity_screen()
			self.x_set_status(sta_ready)
			if not cancelled:
				self.x_show_info('measuring completed', inf_normal)
				self.x_show_result_screen()
			else:
				self.x_show_info('measuring cancelled', inf_normal)

	def quit(self):
		"""Main window close handler"""
		gui.quit()
		if sys.platform != 'win32' and self.style.halt_on_close:
			os.system('halt')

	def run(self):
		"""Run GUI and separate worker thread"""
		app.init()
		if sys.platform != 'win32':
			pygame.mouse.set_visible(False)
		self.show_main_screen()
		self.worker.start()
		self.screen.run_event_loop(self.style.max_fps)		
		app.fini()

if __name__ == '__main__':
	Demo().run()
