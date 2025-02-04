from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyqtgraph import GraphItem, TextItem, mkPen
import glo_var
from math import sqrt



class Cursor_Point(GraphItem):
	def __init__(self, phas):
		self.dragPoint = None
		self.dragOffset = None
		self.textItems = []
		self.region_bef = None
		self.region_aft = None
		self.phas= phas
		GraphItem.__init__(self)


	def setData(self, **kwds):
		self.text = kwds.pop('text', [])
		self.data = kwds
		if 'pos' in self.data:
			npts = self.data['pos'].shape[0]
			self.data['data'] = np.empty(npts, dtype=[('index', int)])
			self.data['data']['index'] = np.arange(npts)
		self.setTexts(self.text)
		self.updateGraph()
		
	def setTexts(self, text):
		for i in self.textItems:
			i.scene().removeItem(i)
		self.textItems = []
		for t in text:
			item = TextItem(t)
			self.textItems.append(item)
			item.setParentItem(self)
		
	def updateGraph(self):

		GraphItem.setData(self, **self.data)
		for i,item in enumerate(self.textItems):
			item.setPos(*self.data['pos'][i])
		

	

	def mouseDragEvent(self, ev):
		if ev.button() != QtCore.Qt.LeftButton:
			ev.ignore()
			return
		
		if ev.isStart():
			# We are already one step into the drag.
			# Find the point(s) at the mouse cursor when the button was first 
			# pressed:
			pos = ev.buttonDownPos()
			pts = self.scatter.pointsAt(pos)
			if len(pts) == 0:
				ev.ignore()
				return
			self.dragPoint = pts[0]
			ind = pts[0].data()[0]
			self.dragOffset = self.data['pos'][ind] - pos
		elif ev.isFinish():
			self.dragPoint = None
			return
		else:
			if self.dragPoint is None:
				ev.ignore()
				return
		
		self.dat = self.scatter.getData() 
		if len(self.dat) > 0 :
			a,b = self.dat
			self.slid.update_phas(a[0], b[0])
			self.legend(a,b)

		ind = self.dragPoint.data()[0]
		self.data['pos'][ind] = ev.pos() + self.dragOffset
		self.updateGraph()
		ev.accept()
		


	def legend(self, a, b, changed = False):
		if not changed:
			if a > glo_var.alpha_star and b > glo_var.beta_star:
				self.region_aft = 'MC'
			elif a> glo_var.alpha_star:
				self.region_aft = 'HD  ' + '\u2161'
			elif b> glo_var.beta_star:
				self.region_aft = 'LD  ' + '\u2161'
			elif b > self.phas.trans_func(a):
				self.region_aft = 'LD  ' + '\u2160'
			else:
				self.region_aft = 'HD  ' + '\u2160'
		else:
			pass
		if self.region_bef != self.region_aft:
			self.region_bef=self.region_aft
			self.legend(a, b, changed = True)
		if changed:
			self.phas.pointer.setPen(None)	
			self.phas.leg.items = []
			self.phas.p5main.plot(pen=None, name=self.region_aft)

	def receive(self, slid, phase):
		self.slid = slid
		# don't need phase






class phase:
	def __init__(self, dphase):
		self.purple = mkPen(QtGui.QColor(20,20,140,255))
		self.red = mkPen(QtGui.QColor(180,0,0,255))
		self.blue = mkPen(QtGui.QColor(20,20,140,255))
		self.roicolor = QtGui.QPen()
		self.roicolor.setBrush(QtGui.QColor(20,20,140,255))

		self.dphase = dphase
		self.p5main = glo_var.MyPW(x="\u03b1",y1="\u03b2",set_range = self.set_range)
		self.p5=self.p5main.plotItem

		self.viewbox = self.p5main.getPlotItem().getViewBox()
		self.viewbox.setBackgroundColor('w')
		self.p5main.coordinate_label = QtGui.QLabel()
		self.frame = glo_var.setframe(self.p5main, width = 1, coordinate_label = self.p5main.coordinate_label)

		self.dphase.addWidget(self.frame)
		self.viewbox.setLimits(xMin = 0, yMin = 0, xMax=1, yMax=1)
		self.set_range()
		
		self.p5main.plotItem.addLegend = glo_var.myaddLegend
		self.p5main.addLegend(self.p5main.plotItem, offset=(0,0.0000001))
		self.leg = self.p5main.plotItem.legend
		self.p5main.setLabel('bottom',"\u03b1",**glo_var.labelstyle)
		self.p5main.setLabel('left',"\u03b2",**glo_var.labelstyle)
		self.initiate()
	def set_range(self):
		self.viewbox.setLimits(xMin = 0, yMin = 0, xMax=1, yMax=1)
		self.viewbox.setRange(xRange=[0,2*glo_var.alpha_star],yRange=[0,2*glo_var.beta_star],padding=0)

	def initiate(self):

		self.value_declaration()
		self.pointer = Cursor_Point(self)

		self.pointer.legend(glo_var.alpha,glo_var.beta)

		self.ablim = 0.5/(1+sqrt(glo_var.l))

		self.bounds1 = np.array([[glo_var.alpha_star,glo_var.beta_star],[1,glo_var.beta_star]])
		self.bounds2 = np.array([[glo_var.alpha_star,glo_var.beta_star],[glo_var.alpha_star,1]])
		self.bounds3 = np.array([[0,0],[glo_var.alpha_star,glo_var.beta_star]])
		self.p5main.plot(self.bounds1)
		self.p5main.plot(self.bounds2)
		self.p5main.plot(self.bounds3)


	def update(self):
		self.p5main.clear()

		self.p5main.addItem(self.pointer)
		self.pointer.setData(pos = np.array([[glo_var.alpha,glo_var.beta]],dtype=float))
		self.pointer.legend(glo_var.alpha,glo_var.beta)

		self.value_declaration()


		if glo_var.alpha > 2*glo_var.alpha_star:
			glo_var.alpha = 2*glo_var.alpha_star
		if glo_var.beta > 2*glo_var.beta_star:
			glo_var.beta = 2*glo_var.beta_star

		HD = TextItem(html='HD', anchor=(glo_var.alpha_star,0.5*glo_var.beta_star), border='w', fill=(255, 0, 0, 250))

		HD.setPos(glo_var.alpha_star,0.5*glo_var.beta_star)
		LD = TextItem(html='LD', anchor=(glo_var.alpha_star*0.3,glo_var.beta_star*1.3), border='w', fill=(0, 255, 0, 200))

		LD.setPos(glo_var.alpha_star*0.3,glo_var.beta_star*1.3)
		MC = TextItem(html='MC', anchor=(glo_var.alpha_star*1.2,glo_var.beta_star*1.3), border='w', fill=(0, 0, 255, 200))
		MC.setPos(glo_var.alpha_star*1.2,glo_var.beta_star*1.3)


		self.bounds1 = np.array([[glo_var.alpha_star,glo_var.beta_star],[1,glo_var.beta_star]])
		self.bounds2 = np.array([[glo_var.alpha_star,glo_var.beta_star],[glo_var.alpha_star,1]])
		linspace=np.linspace(0,glo_var.alpha_star,20)
		trans_line_val=[]
		for i in linspace:
			trans_line_val += [self.trans_func(i)]
		self.p5main.plot(self.bounds1, pen = 'k')
		self.p5main.plot(self.bounds2, pen = 'k')
		self.p5main.plot(linspace,trans_line_val, pen = 'k')


		self.set_range()



	def value_declaration(self):
		self.lambdas_xs, self.lambdas_ys = zip(*sorted(glo_var.lambdas))
		self.lambda_0 = glo_var.lambdas[0][1]
		self.lambda_1 = glo_var.lambdas[ - 1][1]

	def trans_func(self, point):
		self.B = point*(self.lambda_0 - point)/(self.lambda_0 + (glo_var.l -1) * point)
		self.trans_b = - self.lambda_1 +(glo_var.l-1)*self.B
		self.trans_intercal = 0 if pow(self.trans_b,2) - 4*self.B*self.lambda_1 < 0.0000001 else sqrt(pow(self.trans_b,2) - 4*self.B*self.lambda_1)
		self.trans = (-self.trans_b - self.trans_intercal)/2
		return self.trans

	def receive(self, slid):
		self.slid = slid
		self.pointer.receive(slid, self)