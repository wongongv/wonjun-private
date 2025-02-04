
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import glo_var

class myscat(pg.ScatterPlotItem):

	def receive(self, slid, lamb_po):
		self.slid = slid
		self.lamb_po = lamb_po
	def mouseClickEvent(self, ev):
		if ev.button() == QtCore.Qt.LeftButton:
			pts = self.pointsAt(ev.pos())
			if len(pts) > 0:
				self.ptsClicked = pts
				self.index = glo_var.lambdas.index([self.ptsClicked[0]._data[0],self.ptsClicked[0]._data[1]])
				self.sigClicked.emit(self, self.ptsClicked)
				ev.accept()
			else:
				self.lamb_po.lastClicked[0].resetPen()
				self.lamb_po.lastClicked=[]
				ev.ignore()
		
		elif ev.button() == QtCore.Qt.RightButton:
			pts = self.pointsAt(ev.pos())
			if len(pts) > 0:
				self.ptsClicked = pts
				self.index = glo_var.lambdas.index([self.ptsClicked[0]._data[0],self.ptsClicked[0]._data[1]])
				self.raisecontextmenu(pts, ev)
				ev.accept()
			else:
				self.lamb_po.lastClicked[0].resetPen()
				self.lamb_po.lastClicked=[]
				ev.ignore()
		else:
			ev.ignore()


	def mouseDragEvent(self, ev):
		if ev.button() != QtCore.Qt.LeftButton:
			ev.ignore()
			return
		
		if ev.isStart():
			# We are already one step into the drag.
			# Find the point(s) at the mouse cursor when the button was first 
			# pressed:
			pts = self.lamb_po.lastClicked[0]


			if not pts:
				ev.ignore()
				return
			# self.ptsClicked = pts
			# self.index = glo_var.lambdas.index([self.ptsClicked[0]._data[0],self.ptsClicked[0]._data[1]])
			self.dragPoint = pts
			self.dragPoint.setPen('b',width=2)

			# print(pts[0]._data,"data")
			# ind = pts[0]._data[0]

			# self.dragOffset = self.data['pos'][ind] - pos
		elif ev.isFinish():
			self.dragPoint = None
			self.lamb_po.lastClicked=[]
			return
		else:
			if self.dragPoint is None:
				ev.ignore()
				return
		
		self.set_yval(ev.pos()[1])
		# ind = self.dragPoint.data()[0]
		# self.data['pos'][ind] = ev.pos() + self.dragOffset
		# self.updateGraph()
		ev.accept()

		
	def set_yval(self, value):
		self.ptsClicked[0]._data[1] = value
		self.slid.update_lamb_rh(self.index, value, 0)

	def raisecontextmenu(self, point, ev):
		self.menu = Menu(self, point)
		self.menu.popup(ev.screenPos().toQPoint())

class Menu(QtGui.QMenu):
	def __init__(self, item, point):
		QtGui.QMenu.__init__(self)
		self.point = point
		self.item = item
		self.positionMenu = self.addMenu("Change \u03bb")
		self.w=QtGui.QWidget()
		self.l=QtGui.QGridLayout()
		self.w.setLayout(self.l)
		self.fracPosSpin = pg.widgets.SpinBox.SpinBox()
		self.fracPosSpin.setOpts(value=point[0]._data[1], bounds=(0.0, None), step=0.01, decimals=3)
		self.l.addWidget(QtGui.QLabel("\u03bb(x) : "), 0,0)
		self.l.addWidget(self.fracPosSpin, 0, 1)
		self.a = QtGui.QWidgetAction(self)		
		self.a.setDefaultWidget(self.w)
		self.positionMenu.addAction(self.a)
		self.fracPosSpin.sigValueChanging.connect(self.fractionalValueChanged)
		
		
	def fractionalValueChanged(self, x):
		val = self.fracPosSpin.value()
		if val > self.item.lamb_po.lambda_max:
			self.item.lamb_po.lambda_max = val
			# to disable auto rescale
			# self.item.lamb_po.set_range()
		else:
			self.item.lamb_po.lambda_max=max(self.item.lamb_po.lambdas_ys)
			# to disable auto rescale
			# self.item.lamb_po.set_range()
		self.item.set_yval(val)

class lamb_pol:
	def __init__(self,dlamb) : 
		self.dlamb = dlamb
		self.p1main = glo_var.MyPW(x = 'x', y1='\u03bb',set_range = self.set_range, num = 1, set_range_byspbox = self.set_range_byspbox)
		self.p1=self.p1main.plotItem
		self.p1main.setLabel('bottom',"x",**glo_var.labelstyle)
		self.p1main.setLabel('left',"\u03bb",**glo_var.labelstyle)
		self.p1main.set_range = self.set_range

		# to use in clear points

# I didnt use it. Think about it.
		self.font = QtGui.QFont()
		self.font.setBold(True)
		self.viewbox=self.p1main.getViewBox()
		self.viewbox.setBackgroundColor('w')
		# self.viewbox.setLimits(xMin = -0.03, yMin = -0.03, xMax = 1.03)
		self.lambdas_xs, self.lambdas_ys = zip(*sorted(glo_var.lambdas))
		self.lambda_min=min(self.lambdas_ys)
		self.lambda_max=max(self.lambdas_ys)
		self.sp = myscat(size = 7, pen = pg.mkPen(None), brush=pg.mkBrush(100,200,200), symbolPen='w')
		self.lastClicked=[]
		self.p1main.coordinate_label = QtGui.QLabel()
		self.frame = glo_var.setframe(self.p1main, width = 1, coordinate_label = self.p1main.coordinate_label)
		self.dlamb.addWidget(self.frame)
		
		self.range = [[0,self.lambda_max],[0,1.2*self.lambda_max]]
		self.p1main.receive_range(self.range)
		self.set_range()
		

		# self.p1main.scene().mouseMoveEvent = self.mevent
		# self.proxy = pg.SignalProxy(self.p1main.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoveEvent)
		# print(dir(self.p1main.scene()), "p1")
		self.update()

	# def mevent(self, event):
	# 	print(event.button())
	# 	if event.type() == 2:
	# 		print('pressed')

	def set_range(self):
		self.viewbox.setRange(xRange=[0,self.lambda_max],yRange=[0,1.2*self.lambda_max],padding =0.1)
		self.range[0] = [0,self.lambda_max]
		self.range[1] = [0,1.2*self.lambda_max]
		self.p1main.set_spbox_value()
	
	def set_range_byspbox(self):
		self.viewbox.setRange(xRange=self.range[0],yRange=self.range[1],padding =0.1)
	
	def update(self):
		self.p1main.clear()
		self.x, self.y = zip(*sorted(glo_var.lambdas))
		self.curve=pg.PlotCurveItem(np.array(self.x), np.array(self.y))
		self.curve.setPen(pg.mkPen('k',width = glo_var.line_width))
		self.p1main.addItem(self.curve)
		self.sp.setData(self.x,self.y)
		self.sp.sigClicked.connect(self.clicked)
		self.p1main.addItem(self.sp)

	def clicked(self, item, points):
		self.points=points
		for p in self.lastClicked:
			p.resetPen()
		for p in points:
			p.setPen('b', width=2)
		self.lastClicked = points

	def receive(self, slid):
		self.sp.receive(slid, self)