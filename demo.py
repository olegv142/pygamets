#!/usr/bin/python

"""
Generic measuring device GUI example
"""

import env
import app, gui, button, label, battery, progress, window, style
import pygame, sys, os, time, threading, functools
from style import Style

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
		self.style        = style.bind(self)
		self.worker       = threading.Thread(target = self.x_worker)
		self.worker.daemon= True
		self.start_time   = None
		self.start_evt    = threading.Event()
		self.stop_evt     = threading.Event()
		self.status       = sta_none

	def show_main_screen(self):
		"""
		Show main screen with 2 information panels, battery indicator and start button
		"""
		W, H = self.style.screen_w, self.style.screen_h
		self.screen.init_mode((W, H))
		self.s_background = window.BckgWindow()
		status_panel_h = self.style.status_panel_h
		info_panel_h = self.style.info_panel_h
		btn = button.XButton(status_panel_h)
		btn.clicked.connect(self.quit)
		self.s_background.add_child(btn, 0, 0)
		self.s_battery = battery.BatteryIndicator(self.style.batt_width, status_panel_h - 2 * self.style.batt_margin)
		self.s_battery.set_charge(self.style.batt_charge)
		self.s_background.add_child(self.s_battery, W - self.style.batt_width - self.style.batt_margin, self.style.batt_margin)
		self.s_status = label.TextLabel(W - status_panel_h - self.style.batt_width - self.style.batt_margin, status_panel_h, Style(tag='status'))
		self.s_background.add_child(self.s_status, status_panel_h, 0)
		self.s_info = label.TextLabel(W, info_panel_h, Style(tag='info'))
		self.s_background.add_child(self.s_info, 0, H - info_panel_h)
		start_margin = self.style.start_margin
		btn = button.PulseTextButton(W, H - status_panel_h - info_panel_h - 2*start_margin, Style(name='START'))
		btn.clicked.connect(self.start_activity)
		self.s_background.add_child(btn, 0, status_panel_h + start_margin)
		self.screen.show(self.s_background)

	def show_activity_screen(self):
		"""Show activity screen with progress indicator"""
		W, H, margin = self.style.screen_w, self.style.screen_h, self.style.active_margin
		width, height = W - 2*margin, H - self.style.status_panel_h - self.style.info_panel_h
		self.s_action = window.FrameWindow(margin, self.style.status_panel_h, width, height, Style(tag='activity'))
		btn = button.XButton(self.style.close_btn_sz)
		btn.clicked.connect(self.cancel_activity)
		self.s_action.add_child(btn, width - self.style.close_btn_sz, 0)
		progress_sz = int(height * self.style.progress_sz)
		self.s_progress = progress.PieProgressIndicator(progress_sz)
		self.s_action.add_child(self.s_progress, (height - progress_sz) / 2, (height - progress_sz) / 2)
		self.s_remaining = label.TextLabel(width - (height + progress_sz) / 2, progress_sz, Style(tag='remaining'))
		self.s_action.add_child(self.s_remaining, (height + progress_sz) / 2, (height - progress_sz) / 2)
		self.screen.show(self.s_action)

	def x_show_activity_screen(self):
		"""Show activity screen from worker thread"""
		app.instance.add_job(self.show_activity_screen)
		
	def show_progress(self, val, rotating, secs_left = None):
		"""Show progress on activity screen"""
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
		self.s_action.discard()

	def x_close_activity_screen(self):
		"""Close activity screen from worker thread"""
		app.instance.add_job(self.close_activity_screen)

	def show_result_screen(self):
		"""Show results screen"""
		W, H, margin = self.style.screen_w, self.style.screen_h, self.style.result_margin
		width, height = W - 2*margin, H - self.style.status_panel_h - self.style.info_panel_h
		s = window.FrameWindow(margin, self.style.status_panel_h, width, height, Style(tag='result'))
		btn = button.XButton(self.style.close_btn_sz)
		btn.clicked.connect(s.discard)
		s.add_child(btn, width - self.style.close_btn_sz, 0)
		padding = s.style.border + 1
		txt = label.TextLabel(width - 2*padding, height - 2*padding, Style(tag='result', f_color=None))
		txt.set_text('Life is good')
		s.add_child(txt, padding, padding)
		self.screen.show(s)

	def x_show_result_screen(self):
		"""Show results screen from worker thread"""
		app.instance.add_job(self.show_result_screen)

	def start_activity(self):
		"""Start button handler"""
		self.start_evt.set()

	def cancel_activity(self):
		"""Activity screen close button handler"""
		self.stop_evt.set()

	def set_status(self, sta):
		"""Set new status and update status panel accordingly"""
		self.status = sta
		self.s_status.set_text(sta_names[sta], self.style.status_colors[sta])

	def x_set_status(self, sta):
		"""Set new status from worker thread"""
		app.instance.add_job(functools.partial(self.set_status, sta))

	def show_info(self, text, lvl):
		"""Show info on bottom panel"""
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
		if self.style.halt_on_close:
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
