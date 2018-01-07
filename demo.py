#!/usr/bin/python

"""
Generic measuring device GUI example
"""

import env
import app, gui, button, label, battery, progress, window, style
import pygame, sys, time, threading, functools
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
		self.worker       = threading.Thread(target = self.work_loop)
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
		btn.clicked.connect(gui.quit)
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
		self.screen.show(self.s_action)

	def show_progress(self, val, rotating):
		"""Show progress on activity screen"""
		self.s_progress.set_progress(val, rotating)

	def close_activity_screen(self):
		"""Close activity screen"""
		self.s_progress = None
		self.s_action.discard()

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

	def show_info(self, text, lvl):
		"""Show info on bottom panel"""
		self.s_info.set_text(text, self.style.info_colors[lvl])

	def x_initialize(self):
		"""Experiment initialize"""
		time.sleep(1)

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

	def work_loop(self):
		"""
		Worker thread running experiments.
		Note that is uses special asynchronous mechanisms - events and jobs for
		communicating with GUI event loop.
		"""
		app.instance.add_job(functools.partial(self.set_status, sta_initializing))
		app.instance.add_job(functools.partial(self.show_info, 'connecting to device', inf_normal))
		self.x_initialize()
		app.instance.add_job(functools.partial(self.set_status, sta_ready))
		app.instance.add_job(functools.partial(self.show_info, 'connected to device', inf_normal))

		while True:
			self.start_evt.wait()
			self.start_evt.clear()
			self.stop_evt.clear()

			app.instance.add_job(functools.partial(self.set_status, sta_busy))
			app.instance.add_job(functools.partial(self.show_info, 'measurement starting', inf_normal))
			app.instance.add_job(self.show_activity_screen)

			ini_progress, fin_progress = self.style.ini_progress, self.style.fin_progress
			progress = ini_progress
			app.instance.add_job(functools.partial(self.show_progress, progress, True))

			xtime = self.x_prepare()
			app.instance.add_job(functools.partial(self.show_info, 'measuring stuff', inf_normal))
			self.start_time = time.time()
			cancelled = False

			while True:
				if self.stop_evt.is_set():
					cancelled = True
					break
				if self.x_run():
					break
				progress = ini_progress + (1 - ini_progress - fin_progress) * (time.time() - self.start_time) / xtime
				app.instance.add_job(functools.partial(self.show_progress, progress, False))

			if not cancelled:
				app.instance.add_job(functools.partial(self.show_progress, progress, True))
				app.instance.add_job(functools.partial(self.show_info, 'processing results', inf_normal))
				self.x_complete()

			app.instance.add_job(self.close_activity_screen)
			app.instance.add_job(functools.partial(self.set_status, sta_ready))
			if not cancelled:
				app.instance.add_job(functools.partial(self.show_info, 'measuring completed', inf_normal))
				app.instance.add_job(self.show_result_screen)
			else:
				app.instance.add_job(functools.partial(self.show_info, 'measuring cancelled', inf_normal))

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
