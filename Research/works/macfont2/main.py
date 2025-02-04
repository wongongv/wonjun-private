
import sys
from pyqtgraph.Qt import QtGui, QtCore, QtSvg
import numpy as np
import pyqtgraph as pg
import glo_var
import lamb_pol
import slider
import rho
import jbeta
import jalpha
import phase
import csv
import pyqtgraph.widgets.RemoteGraphicsView
from pyqtgraph.widgets.GraphicsLayoutWidget import GraphicsLayoutWidget
import pyqtgraph.widgets.RemoteGraphicsView
from pyqtgraph.dockarea import Dock, DockArea
import os.path
from os import makedirs
from copy import deepcopy









def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")
	return os.path.join(base_path, relative_path)
logo = resource_path("logo.png")




class MyPW(pg.PlotWidget):
		
	def mousePressEvent(self, event):
		self.__mousePressPos = None
		self.__mouseMovePos = None
		if event.button() == QtCore.Qt.LeftButton:
			self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
			self.__mousePressPos = event.globalPos()
			self.__mouseMovePos = event.globalPos()


	def mouseMoveEvent(self, event):
		if event.buttons() == QtCore.Qt.LeftButton:
			# adjust offset from clicked point to origin of widget

			self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowStaysOnTopHint)
			currPos = self.mapToGlobal(self.pos())
			globalPos = event.globalPos()
			diff = globalPos - self.__mouseMovePos
			newPos = self.mapFromGlobal(currPos + diff)
			self.move(newPos)

			self.__mouseMovePos = globalPos


	def mouseReleaseEvent(self, event):
		if self.__mousePressPos is not None:
			moved = event.globalPos() - self.__mousePressPos 
			if moved.manhattanLength() > 3:
				event.ignore()
				return



class MainWindow(QtGui.QMainWindow):
# for dock
	def __init__(self,parent=None):

		from pyqtgraph import exporters
		exporters.Exporter.register = self.modified_register

		QtGui.QMainWindow.__init__(self, parent)
	
		self.setWindowIcon(QtGui.QIcon(logo))
		self.setWindowTitle('CIVET')  

		self.setGeometry(200,143,1574,740)
		pg.setConfigOption('background', QtGui.QColor(215,214,213,255))
		pg.setConfigOption('foreground', 'k')
		palette = QtGui.QPalette()
		palette.setColor(QtGui.QPalette.Background, QtGui.QColor(215,214,213,255))
		self.setPalette(palette)


		self.mainframe = QtGui.QFrame()


		self.copen=0
		self.sopen=0
		self.ropen=0
		self.gridstate=0
		self.current_docks=[]


		self.loadaction = QtGui.QAction("&Open",self)
		self.loadaction.setShortcut("Ctrl+O")
		self.loadaction.setStatusTip("Open File")
		self.loadaction.triggered.connect(self.loaddata)


		self.exportaction = QtGui.QAction("&Export",self)
		self.exportaction.setShortcut("Ctrl+E")
		self.exportaction.setStatusTip("Export to a folder")
		self.exportaction.triggered.connect(self.exportdata)

		self.viewaction1 = QtGui.QAction("&Grid View 1",self)
		self.viewaction1.setStatusTip("Grid View 1")
		self.viewaction1.triggered.connect(self.grid_view_1)

		self.viewaction2 = QtGui.QAction("&Grid View 2",self)
		self.viewaction2.setStatusTip("Grid View 2")
		self.viewaction2.triggered.connect(self.grid_view_2)

		self.about = QtGui.QAction("&Info", self)
		self.about.setStatusTip("Info")
		self.about.triggered.connect(self.about_info)

		self.mainMenu = self.menuBar()
		self.fileMenu = self.mainMenu.addMenu("&File")
		self.fileMenu.addAction(self.loadaction)
		self.fileMenu.addAction(self.exportaction)

		self.viewMenu = self.mainMenu.addMenu("&Display")
		self.viewMenu.addAction(self.viewaction1)
		self.viewMenu.addAction(self.viewaction2)

		self.aboutMenu = self.mainMenu.addMenu("&About")
		self.aboutMenu.addAction(self.about)
		
		self.maketoolbar()




		self.area = DockArea()
		
		self.drho = Dock("\u03c1")
		self.dlamb=Dock("\u03bb")
		self.dalpha=Dock("\u03b1")
		self.dbeta=Dock("\u03b2")
		self.dphase=Dock("Phase")
		self.dcontrols=Dock("Controls")


		self.layout = QtGui.QHBoxLayout()
		self.layout.addWidget(self.area)
		self.mainframe.setLayout(self.layout)
		self.mainframe.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
		self.mainframe.setLineWidth(8)


# all those have different relative positions so made bunch of functions, not one.
	def modified_register(self,cls):


		exporters.Exporter.Exporters.append(None)

	def dlambadd(self):
		try:
			self.area.addDock(self.dlamb,'bottom', self.drho)
		except:
			try:
				self.area.addDock(self.dlamb,'left',self.dphase)
			except:
				self.area.addDock(self.dlamb,'left')

	def drhoadd(self):
		try:
			self.area.addDock(self.drho,'top', self.dlamb)
		except:
			try:
				self.area.addDock(self.drho,'left',self.dalpha)
			except:
				self.area.addDock(self.drho,'left')

	def dalphaadd(self):
		try:
			self.area.addDock(self.dalpha,'left', self.dbeta)
		except:
			try:
				self.area.addDock(self.dalpha,'right',self.drho)
			except:
				try:
					self.area.addDock(self.dalpha,'top',self.dphase)
				except:
					self.area.addDock(self.dalpha,'left')

	def dbetaadd(self):
		try:
			self.area.addDock(self.dbeta,'top', self.dcontrols)
		except:
			try:
				self.area.addDock(self.dbeta,'right',self.dalpha)
			except:
				self.area.addDock(self.dbeta,'right')

	def dphaseadd(self):
		try:
			self.area.addDock(self.dphase,'left', self.dcontrols)
		except:
			try:
				self.area.addDock(self.dphase,'bottom',self.dalpha)
			except:
				try:
					self.area.addDock(self.dphase,'right',self.dlamb)
				except:
					self.area.addDock(self.drho,'bottom')

	def dcontrolsadd(self):
		try:
			self.area.addDock(self.dcontrols,'right', self.dphase)
		except:
			try:
				self.area.addDock(self.dcontrols,'bottom',self.dbeta)
			except:
				self.area.addDock(self.dcontrols,'right')


	def checkbox_init(self):
		self.dock_on = []

		self.cwindow = QtGui.QMainWindow()
		self.cwindow.setWindowIcon(QtGui.QIcon(logo))
		self.cwindow.setWindowTitle('Plots')  

		self.boxeswidget=QtGui.QWidget(self.cwindow)
		checkbox_layout = QtGui.QGridLayout(self.boxeswidget)
		self.ch_lamb=QtGui.QCheckBox(self.boxeswidget)
		self.ch_lamb.setText('\u03bb')
		self.ch_lamb.setChecked(True)
		self.ch_lamb.stateChanged.connect(lambda : self.dlamb.close() if not self.ch_lamb.isChecked() else self.dlambadd())

		self.ch_rho=QtGui.QCheckBox(self.boxeswidget)
		self.ch_rho.setText('\u03c1')
		self.ch_rho.setChecked(True)
		self.ch_rho.stateChanged.connect(lambda : self.drho.close() if not self.ch_rho.isChecked() else self.drhoadd())

		self.ch_alpha=QtGui.QCheckBox(self.boxeswidget)
		self.ch_alpha.setText('\u03b1')
		self.ch_alpha.setChecked(True)
		self.ch_alpha.stateChanged.connect(lambda : self.dalpha.close() if not self.ch_alpha.isChecked() else self.dalphaadd())

		self.ch_beta=QtGui.QCheckBox(self.boxeswidget)
		self.ch_beta.setText('\u03b2')
		self.ch_beta.setChecked(True)
		self.ch_beta.stateChanged.connect(lambda : self.dbeta.close() if not self.ch_beta.isChecked() else self.dbetaadd())

		self.ch_phase=QtGui.QCheckBox(self.boxeswidget)
		self.ch_phase.setText('Phase')
		self.ch_phase.setChecked(True)
		self.ch_phase.stateChanged.connect(lambda : self.dphase.close() if not self.ch_phase.isChecked() else self.dphaseadd())

		self.ch_controls=QtGui.QCheckBox(self.boxeswidget)
		self.ch_controls.setText('Controls')
		self.ch_controls.setChecked(True)
		self.ch_controls.stateChanged.connect(lambda : self.dcontrols.close() if not self.ch_controls.isChecked() else self.dcontrolsadd())


		checkbox_layout.addWidget(self.ch_rho,0,0,1,1)
		checkbox_layout.addWidget(self.ch_lamb,1,0,1,1)
		checkbox_layout.addWidget(self.ch_alpha,0,1,1,1)
		checkbox_layout.addWidget(self.ch_phase,1,1,1,1)
		checkbox_layout.addWidget(self.ch_beta,0,2,1,1)
		checkbox_layout.addWidget(self.ch_controls,1,2,1,1)	
		self.cwindow.setCentralWidget(self.boxeswidget)		


	def checkbox(self):
		if self.copen == 0:
			self.check_current_docks()
			self.closed_docks = []

			for i in self.docklist:
				if i not in self.current_docks:
					self.closed_docks+=[i]
			for i in self.closed_docks:
				eval(i[:5] + "ch_" + i[6:]).setChecked(False)

			self.cwindow.show()
			self.copen = 1
		else:
			self.cwindow.hide()
			self.copen = 0

	def about_info(self):
		
		self.awindow = QtGui.QMainWindow()
		self.awindow.setWindowIcon(QtGui.QIcon(logo))
		self.awindow.setWindowTitle('About')  
		labels=QtGui.QWidget(self.awindow)
		labels_layout = QtGui.QVBoxLayout(labels)
		self.line0 = QtGui.QLabel()
		self.line1 = QtGui.QLabel("CIVET: Current Inspired Visualization and Evaluation of the")
		self.line2 = QtGui.QLabel()
		self.line3 = QtGui.QLabel("Totally asymmetric simple exclusion process (TASEP)")
		self.line4 = QtGui.QLabel()
		self.line5 = QtGui.QLabel("Copyright (c) 2018,")
		self.line6 = QtGui.QLabel()
		self.line7 = QtGui.QLabel("Wonjun Son, Dan D. Erdmann-Pham,  Khanh Dao Duc, Yun S. Song")
		self.line8 = QtGui.QLabel()
		self.line9 = QtGui.QLabel("All rights reserved.")
		self.line10 = QtGui.QLabel()
		
		for i in range(11):
			eval("self.line" + str(i)).setAlignment(QtCore.Qt.AlignCenter)
			labels_layout.addWidget(eval("self.line" + str(i)))
		self.awindow.setCentralWidget(labels)
		self.awindow.show()

	def exportdata(self):



		


		self.dialog = QtGui.QFileDialog()
		self.dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)
		self.dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)

		folder_name = self.dialog.getSaveFileName(self, "Save Directory")
		filepath = os.path.join(os.path.abspath(os.sep), folder_name)
		if not os.path.exists(filepath):
			makedirs(filepath)

		# arr = QtCore.QByteArray()
		# buf = QtCore.QBuffer(arr)
		# svg = QtSvg.QSvgGenerator()
		# svg.setOutputDevice(buf)
		# dpi = QtGui.QDesktopWidget().physicalDpiX()
		# svg.setResolution(dpi)


		svg = QtSvg.QSvgGenerator()
		svg.setFileName("hh")
		svg.setSize(QtCore.QSize(2000, 2000))
		svg.setViewBox(self.rect())
		svg.setTitle("SVG svg Example Drawing")
		svg.setDescription("An SVG drawing created by the SVG Generator ")

		p = QtGui.QPainter()
		p.begin(svg)
		try:
			self.render(p)
		finally:
			p.end()
		# gen.setViewBox(QtGui.QRect(0, 0, 200, 200));
		# gen.setTitle(tr("SVG Gen Example Drawing"));
		# gen.setDescription(tr("An SVG drawing created by the SVG Generator ""Example provided with Qt."));


		lambda_data=os.path.join(filepath, "Lambda_data.csv")
		with open(lambda_data, "w") as output:
			try:
				writer = csv.writer(output, lineterminator='\n')
				for val in np.array(glo_var.lambdas)[:,1]:
					writer.writerow([val])  
			except:
				pass

		summary=os.path.join(filepath, "Summary.csv")
		with open(summary, "w") as output:
			try:
				writer = csv.writer(output, delimiter='\t' ,lineterminator='\n')
				writer.writerow(["alpha",glo_var.alpha])
				writer.writerow(["beta",glo_var.beta])
				writer.writerow(["l",glo_var.l])
				writer.writerow(["Phase",self.phas.pointer.region_aft])
			except:
				pass

		# for name, pitem in self.pltlist:
		# 	self.exportimg(pitem,os.path.join(filepath,name + ".svg"))
		# 	# self.exportimg(pitem,os.path.join(filepath,name + ".png"))


		currentanddensity=os.path.join(filepath, "Current & Density.csv")
		with open(currentanddensity, "w") as output:
			writer = csv.writer(output, delimiter='\t' ,lineterminator='\n')
			# combine alpha, beta    pre and post. Do it here to lessen the computation
			alpha_x_data = np.concatenate([np.array(self.jalph.alphas_pre), np.linspace(self.jalph.trans_point,1,2)])
			alpha_j_data = np.concatenate([self.jalph.j_l_values, np.array([self.jalph.jpost] * 2) ])
			alpha_rho_data = np.array(self.jalph.rho_avg_pre + self.jalph.rho_avg_post)

			beta_x_data = np.concatenate([np.array(self.jbet.betas_pre), np.linspace(self.jbet.trans_point,1,2)])
			beta_j_data = np.concatenate([self.jbet.j_r_values,np.array([self.jbet.jpost] * 2 )])
			beta_rho_data = np.array(self.jbet.rho_avg_pre + self.jbet.rho_avg_post)
			
			alpha_data = np.vstack([alpha_x_data,alpha_j_data,alpha_rho_data])
			beta_data = np.vstack([beta_x_data,beta_j_data,beta_rho_data])

			writer.writerow(["alpha","Current","Average Density",'\t','\t',"beta","Current","Average Density"])
			for i in range(len(alpha_x_data)):
				writer.writerow(list(alpha_data[:,i]) + [''] *2 + list(beta_data[:,i]))
			writer.writerow('\n')
			writer.writerow(['beta',glo_var.beta,'','','','alpha',glo_var.alpha,''])
			writer.writerow(['transition point',self.jalph.trans_point,'','','','transition point',self.jbet.trans_point,''])



		self.pdfgroup1 = ['Lambda_fig','Density_fig']
		self.pdfgroup2 = ['Current_alpha_fig','Current_beta_fig']

	
		for name, pitem in self.pltlist:
			# self.exportimg(pitem,os.path.join(filepath,name + ".png"))
			path = os.path.join(filepath,name + ".svg")
#			if name == 'Current_alpha_fig':
#				self.jalph.p3.setLabel('right',"\u2329\u03c1 \u232a",**glo_var.labelstyle)
#				self.jalph.p3main.plotItem.legend.items=[]
#				self.jalph.p3.plot(pen=self.jalph.jpen, name='J')
#				self.jalph.p3.plot(pen=self.jalph.rho_dash, name='\u2329\u03c1 \u232a')

#			elif name == 'Current_beta_fig':
#				self.jbet.p4.setLabel('right',"\u2329\u03c1 \u232a",**glo_var.labelstyle)
#				self.jbet.p4main.plotItem.legend.items=[]
#				self.jbet.p4.plot(pen=self.jbet.jpen, name='J')
#				self.jbet.p4.plot(pen=self.jbet.rho_dash, name='\u2329\u03c1 \u232a')
			self.exportimg(pitem,path)
		
			if name in self.pdfgroup1:  
				self.makepdf(path,os.path.join(filepath,name + ".pdf"),500,260,20,240)
			elif name == 'Current_alpha_fig':
				self.makepdf(path,os.path.join(filepath,name + ".pdf"),350,280,30,230)
#				self.jalph.p3.setLabel('right',"\u2329 \u03c1 \u232a",**glo_var.labelstyle)
#				self.jalph.p3main.plotItem.legend.items=[]
#				self.jalph.p3.plot(pen=self.jalph.jpen, name='J')
#				self.jalph.p3.plot(pen=self.jalph.rho_dash, name='\u2329 \u03c1 \u232a')
			elif name == 'Current_beta_fig':
				self.makepdf(path,os.path.join(filepath,name + ".pdf"),350,280,30,230)
#				self.jbet.p4.setLabel('right',"\u2329 \u03c1 \u232a",**glo_var.labelstyle)
#				self.jbet.p4main.plotItem.legend.items=[]
#				self.jbet.p4.plot(pen=self.jbet.jpen, name='J')
#				self.jbet.p4.plot(pen=self.jbet.rho_dash, name='\u2329 \u03c1 \u232a')
			
			else:
				self.makepdf(path,os.path.join(filepath,name + ".pdf"),410,330,10,300)

			os.remove(path)

	def makepdf(self,path,name,x,y,z,q):


		from svglib.svglib import svg2rlg
		from reportlab.pdfgen import canvas
		from reportlab.graphics import renderPDF
		rlg = svg2rlg(path)
		rlg.scale(0.8,0.8)
		c = canvas.Canvas(name)
		c.setPageSize((x, y))
		renderPDF.draw(rlg, c, z, q)
		c.showPage()
		c.save()	
			
	def exportimg(self,img,path):
		# self.img = pg.exporters.ImageExporter(img)
		# self.img.export(path)
		self.svg = pg.exporters.SVGExporter(img)
		self.svg.export(fileName=path)

	def maketoolbar(self):
		self.state = None
		self.titlebarstate = 1
		self.toolbar = self.addToolBar("Toolbar")


		home = QtGui.QAction(QtGui.QIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ComputerIcon)),'Toggle Grid View',self)
		home.triggered.connect(self.toggle_grid_view)
		self.toolbar.addAction(home)

		fix = QtGui.QAction(QtGui.QIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_ArrowDown)),'Fix current layout',self)
		fix.triggered.connect(self.fixdock)
		self.toolbar.addAction(fix)
		
		self.savedockandvaluesinit()
		save = QtGui.QAction(QtGui.QIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_FileDialogListView)),'Save current layout',self)
		save.triggered.connect(self.popsavedockandvalues)
		self.toolbar.addAction(save)

		self.restoredockandvaluesinit()
		restore = QtGui.QAction(QtGui.QIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_BrowserReload)),'Restore saved layout',self)
		restore.triggered.connect(self.poprestoredockandvalues)
		self.toolbar.addAction(restore)
		
		self.checkbox_init()
		checkbox = QtGui.QAction(QtGui.QIcon(QtGui.QApplication.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView)),'Open & close specific windows',self)
		checkbox.triggered.connect(self.checkbox)
		self.toolbar.addAction(checkbox)
	


	def fixdock(self):
		if self.titlebarstate == 1:
			self.dlamb.hideTitleBar()
			self.drho.hideTitleBar()
			self.dalpha.hideTitleBar()	
			self.dbeta.hideTitleBar()
			self.dcontrols.hideTitleBar()
			self.dphase.hideTitleBar()
			self.titlebarstate = 0

		else:
			self.dlamb.showTitleBar()
			self.drho.showTitleBar()
			self.dalpha.showTitleBar()	
			self.dbeta.showTitleBar()
			self.dcontrols.showTitleBar()
			self.dphase.showTitleBar()
			self.titlebarstate = 1

	def savedockandvaluesinit(self):

		self.swindow = QtGui.QMainWindow()
		self.swindow.setWindowIcon(QtGui.QIcon(logo))
		self.swindow.setWindowTitle('Save')  

		boxeswidget=QtGui.QWidget(self.swindow)
		checkbox_layout = QtGui.QGridLayout(boxeswidget)

		self.sa_dock=QtGui.QCheckBox(boxeswidget)
		self.sa_dock.setText('Grid View')
		self.sa_dock.setChecked(True)

		self.sa_values=QtGui.QCheckBox(boxeswidget)
		self.sa_values.setText('Values')
		self.sa_values.setChecked(True)

		self.save_button = QtGui.QPushButton('Save', self)
		self.save_button.clicked.connect(self.savedockandvalues)
		
		checkbox_layout.addWidget(self.sa_dock,0,0,1,1)
		checkbox_layout.addWidget(self.sa_values,0,1,1,1)
		checkbox_layout.addWidget(self.save_button,1,0,1,2)
		
		self.swindow.setCentralWidget(boxeswidget)		

	def restoredockandvaluesinit(self):

		self.rwindow = QtGui.QMainWindow()
		self.rwindow.setWindowIcon(QtGui.QIcon(logo))
		self.rwindow.setWindowTitle('Restore')  

		boxeswidget=QtGui.QWidget(self.rwindow)
		checkbox_layout = QtGui.QGridLayout(boxeswidget)


		self.re_dock=QtGui.QCheckBox(boxeswidget)
		self.re_dock.setText('Grid View')
		self.re_dock.setChecked(True)

		self.re_values=QtGui.QCheckBox(boxeswidget)
		self.re_values.setText('Values')
		self.re_values.setChecked(True)

		self.restore_button = QtGui.QPushButton('Restore', self)
		self.restore_button.clicked.connect(self.restoredockandvalues)
		
		checkbox_layout.addWidget(self.re_dock,0,0,1,1)
		checkbox_layout.addWidget(self.re_values,0,1,1,1)
		checkbox_layout.addWidget(self.restore_button,1,0,1,2)
		
		self.rwindow.setCentralWidget(boxeswidget)

	def savedockandvalues(self):
		if self.sa_values.checkState:
			self.savedlambdas=deepcopy(glo_var.lambdas)
			self.savedalpha=glo_var.alpha
			self.savedbeta=glo_var.beta
			self.savedl=glo_var.l
		if self.sa_dock.checkState:
			self.saved_state = []
			self.state = self.area.saveState()
			self.saved_state = self.check_current_docks()[:]

		self.sopen = 0
		self.swindow.hide()
	def popsavedockandvalues(self):
		if self.sopen == 0:
			self.swindow.show()
			self.sopen = 1
		
		else:
			self.swindow.hide()
			self.sopen = 0
		
	def poprestoredockandvalues(self):
		if self.ropen == 0:
			self.rwindow.show()
			self.ropen = 1
		
		else:
			self.rwindow.hide()
			self.ropen = 0
		
	def restoredockandvalues(self):
		if self.re_values.checkState:
			glo_var.lambdas = deepcopy(self.savedlambdas)
			glo_var.alpha = self.savedalpha
			glo_var.beta = self.savedbeta
			glo_var.l = self.savedl

			self.lamb_po.update()
			self.rh.update()
			self.phas.update()
			self.jalph.update()
			self.jbet.update()
			self.slid.update_alpha_slid(self.slid.ws[0])
			self.slid.update_beta_slid(self.slid.ws[1])
			self.slid.update_l_slid(self.slid.ws[2])

		if self.re_dock.checkState:

			if self.state != None:
				closed_docks=[]
				self.check_current_docks()
				# Notice after below, current dock != real current dock. But it doesn't matter since we call check current dock every time.
				for i in self.current_docks:
					if i not in self.saved_state:
						eval(i).close()
				for i in self.saved_state:
					if i not in self.current_docks:
						eval(i+"add")()
				self.area.restoreState(self.state)
		self.ropen = 0
		self.rwindow.hide()

	def realinit(self):
		self.clear_buttons = ["self.lamb_po.p1main.coordinate_label.setText(\"\")",
		"self.rh.p2main.coordinate_label.setText(\"\")",
		"self.jalph.p3main.coordinate_label.setText(\"\")",
		"self.jbet.p4main.coordinate_label.setText(\"\")",
		"self.phas.p5main.coordinate_label.setText(\"\")"]
		
		glo_var.pass_main(self)

		self.docklist = ['self.drho','self.dlamb','self.dalpha','self.dbeta','self.dphase','self.dcontrols']
		self.area = DockArea()
		self.drho = Dock("Particle Density \u2374",closable = True)
		self.dlamb=Dock("Hopping Rate \u03bb", closable = True)
		self.dphase=Dock("Phase Diagram", closable = True)
		self.dcontrols=Dock("Controls", closable = True)
		self.dalpha=Dock("Current J and average density \u27e8\u2374\u27e9 as a function of \u03b1", closable = True)
		self.dbeta=Dock("Current J and average density \u27e8\u2374\u27e9 as a function of \u03b2", closable = True)

		self.layout = QtGui.QHBoxLayout()
		self.layout.addWidget(self.area)
		self.mainframe.setLayout(self.layout)
		self.mainframe.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Raised)
		self.mainframe.setLineWidth(8)

		pg.setConfigOptions(antialias=True)

		self.rh=rho.rho(self.drho)
		self.jalph = jalpha.jalpha(self.dalpha, self.rh)
		self.jbet = jbeta.jbeta(self.dbeta, self.rh)
		self.phas=phase.phase(self.dphase)
		self.lamb_po = lamb_pol.lamb_pol(self.dlamb)
		self.slid=slider.Widget(self.dcontrols, self.lamb_po,self.phas, self.rh, self.jbet,self.jalph)
		self.lamb_po.receive(self.slid)


		# default values to restore is input
		self.savedlambdas=glo_var.lambdas[:]
		self.savedalpha=glo_var.alpha
		self.savedbeta=glo_var.beta
		self.savedl=glo_var.l

		self.pltlist = [['Lambda_fig', self.lamb_po.p1], ['Density_fig',self.rh.p2], ['Current_alpha_fig', self.jalph.plotitemtoexport], ['Current_beta_fig',self.jbet.plotitemtoexport], ['Phase_fig',self.phas.p5]]

		self.grid_view_1()

		self.setCentralWidget(self.area)

		print(dir(self.area))
		print(self.area.childrenRect(), "childrenRect")
		print(self.area.contentsRect(),"contentesRect")
		print(self.area.rect())
	def check_current_docks(self):
		self.current_docks=[]
		for i in self.docklist:
			if self.area.getContainer(eval(i)):
				self.current_docks+=[i]
			else:
				pass
		return self.current_docks

	def toggle_grid_view(self):
		if self.gridstate ==0:
			self.grid_view_2()
			self.gridstate = 1
		else:
			self.grid_view_1()
			self.gridstate = 0

	def grid_view_1(self):
		for i in self.docklist:
			try:
				eval(i).close()
			except:
				pass

		self.drho.setMinimumSize(652,370)
		self.dlamb.setMinimumSize(652,370)
		self.dphase.setMinimumSize(487,465)
		self.dcontrols.setMinimumSize(487,275)
		self.dalpha.setMinimumSize(435,370)
		self.dbeta.setMinimumSize(435,370)

		self.area.addDock(self.drho, 'left')
		self.area.addDock(self.dlamb,'bottom', self.drho)
		self.area.addDock(self.dphase,'right')
		self.area.addDock(self.dcontrols,'bottom', self.dphase)
		self.area.addDock(self.dalpha,'right')
		self.area.addDock(self.dbeta,'bottom', self.dalpha)		

		self.drho.setMinimumSize(0,0)
		self.dlamb.setMinimumSize(0,0)
		self.dphase.setMinimumSize(0,0)
		self.dcontrols.setMinimumSize(0,0)
		self.dalpha.setMinimumSize(0,0)
		self.dbeta.setMinimumSize(0,0)


	def grid_view_2(self):
		for i in self.docklist:
			try:
				eval(i).close()
			except:
				pass
		self.area.addDock(self.drho, 'top')
		self.area.addDock(self.dlamb,'bottom', self.drho)
		self.area.addDock(self.dphase,'bottom')
		self.area.addDock(self.dcontrols, 'left', self.dphase)
		self.area.addDock(self.dalpha,'right')
		self.area.addDock(self.dbeta,'bottom', self.dalpha)



	def opengraphs(self):
		self.mn = main.main_class(app)
		self.window.hide()

	def loaddata(self):
		name = QtGui.QFileDialog.getOpenFileName(self, 'Open File', '.','text (*.txt *.csv)')
		if name == "" :
			pass
		else:
			self.read_file(name)
			self.realinit()

	def read_file(self, input):
		global ison 
		temp=[]
		if ison == 0:
			ison = 1
		else:
			self.setCentralWidget(None)
			glo_var.initialize()


		if input[-3:] == 'csv':
			with open(input, newline='') as csvfile:
				spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
				lis = []
				for j in spamreader:
					lis += j
				num_of_inputs = len(lis)
				glo_var.lambdas_degree = num_of_inputs
				for i in range(num_of_inputs):
					glo_var.lambdas += [[i/(num_of_inputs - 1), round(eval(lis[i]),2)]]
			glo_var.alpha = 0.04
			glo_var.beta = 0.04
			glo_var.l = 1

		elif input[-3:] == 'txt':
			f = open(input,'r')
 # Breaks the loop i 
			try:
				temp=[]
				while(True):
					T = f.readline().strip()
					temp +=[[glo_var.lambdas_degree,round(eval(T),2)]]
			except:
				for x,y in temp:
					glo_var.lambdas += [[x/(glo_var.lambdas_degree - 1),y]]
			glo_var.l = 1

		else:
			err = QtGui.QMessageBox(self.win)
			err.setIcon(QMessageBox().Warning)
			err.setText("Please select txt or csv file Format")
			err.setWindowTitle("File Format Error")
			err.setStandardButtons(QMessageBox.Ok)
			err.buttonClicked.connect()



	def eventFilter(self, source, event):
		if event.type() == QtCore.QEvent.MouseMove:
			if event.buttons() == QtCore.Qt.NoButton:
				pos = event.pos()
				if self.toolbar.rect().contains(pos) or not self.area.rect().contains(pos):
					self.clear_points()
			else:
				pass
		return QtGui.QMainWindow.eventFilter(self, source, event)

	def clear_points(self, exclude = None):
		if not exclude:
			for x in self.clear_buttons:
				eval(x)
		else:
			for x in self.clear_buttons[:exclude - 1] + self.clear_buttons[exclude:]:	
				eval(x)


if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)




	ison = 0
	# window = MainWindow()
	# window.show()
	main = MainWindow()
	app.installEventFilter(main)

	main.show()
	sys.exit(app.exec_())
