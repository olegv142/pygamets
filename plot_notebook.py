import gui, plot, button, label, style, utils
from frame import Frame

class PlotNotebook(gui.Window):
	"""The window showing the set of X,Y data plots"""
	_required_attrs = ('panel_size',)

	def __init__(self, W, H, st = None):
		self.style = style.bind(self, st)
		gui.Window.__init__(self, 0, 0, Frame(W, H, self.style.copy()))
		xbtn = button.XButton(self.style.panel_size, self.style.copy())
		xbtn.clicked.connect(self.close)
		utils.add_top_right(self, xbtn)
		pbtn = button.TextButton(self.style.panel_size, self.style.panel_size, self.style.copy(name='<'))
		pbtn.clicked.connect(self.prev)
		utils.add_top_left(self, pbtn)
		self.count = label.TextLabel(self.style.panel_size, self.style.panel_size, self.style.copy(tag='count'))
		utils.add_top_left(self, self.count, next_to = pbtn)
		nbtn = button.TextButton(self.style.panel_size, self.style.panel_size, self.style.copy(name='>'))
		nbtn.clicked.connect(self.next)
		utils.add_top_left(self, nbtn, next_to = self.count)
		self.info = label.TextLabel(xbtn.left() - nbtn.right(), self.style.panel_size, self.style.copy(tag='info'))
		utils.add_top_left(self, self.info, next_to = nbtn)
		iW, iH = self.int_size()
		self.plot = plot.PlotView(iW, iH - self.style.panel_size, self.style.copy())
		utils.add_left_bottom(self, self.plot)
		self.plots = []
		self.cur_plot = None

	def next(self):
		if not self.plots:
			return
		assert self.cur_plot is not None
		if self.cur_plot + 1 < len(self.plots):
			self._show_plot(self.cur_plot + 1)

	def prev(self):
		if not self.plots:
			return
		assert self.cur_plot is not None
		if self.cur_plot > 0:
			self._show_plot(self.cur_plot - 1)

	def _show_plot(self, i):
		assert 0 <= i < len(self.plots)
		self.cur_plot = i
		X, Y, descr = self.plots[i]
		self.plot.set_data((X, Y))
		self.info.set_text(descr)
		self.count.set_text('%d/%d' % (i + 1, len(self.plots)))

	def add_plot(self, X, Y, descr):
		self.plots.append((X, Y, descr))
		self._show_plot(len(self.plots) - 1)

	def clear_plots(self):
		self.plots = []
		self.cur_plot = None
		self.plot.set_data(None)
		self.info.set_text(None)
		self.count.set_text(None)
