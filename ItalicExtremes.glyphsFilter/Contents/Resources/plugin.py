# encoding: utf-8

###########################################################################################################
#
#
# Filter with dialog Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Filter%20with%20Dialog
#
# For help on the use of Interface Builder:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates
#
#
###########################################################################################################

from __future__ import division, print_function
import objc
from math import atan2, degrees, hypot
from AppKit import NSBundle
from GlyphsApp import Glyphs, GSFont
from GlyphsApp.plugins import FilterWithDialog
from Foundation import NSPoint, NSAffineTransform


bundle = NSBundle.bundleForClass_(GSFont.__class__)
objc.initFrameworkWrapper("GlyphsCore", frameworkIdentifier="com.schriftgestaltung.GlyphsCore", frameworkPath=bundle.bundlePath(), globals=globals())


try:
	TimesOfBezier = GSExtremeTimesOfBezier
except:
	TimesOfBezier = GSExtremTimesOfBezier  # fallback for <= 3.1


AddI = 0
AddHV = 1


class ItalicExtremes(FilterWithDialog):

	dialog = objc.IBOutlet()

	def loadPlugin(self):
		self.menuName = "Italic Extremes"
		self.actionButtonLabel = "Add Nodes"
		self.keyboardShortcut = None
		self.loadNib('dialog', __file__)

	@objc.python_method
	def start(self):
		Glyphs.registerDefault('com.joachimvu.ItalicExtremes.angles', Glyphs.font.selectedFontMaster.italicAngle)
		Glyphs.defaults['com.joachimvu.ItalicExtremes.option'] = AddI

	@objc.IBAction
	def editAnglesCallback_(self, sender):
		self.update()

	@objc.IBAction
	def revertAnglesCallback_(self, sender):
		Glyphs.defaults['com.joachimvu.ItalicExtremes.angles'] = Glyphs.font.selectedFontMaster.italicAngle
		self.update()

	def tabView_didSelectTabViewItem_(self, tabView, item):
		self.update()

	@objc.IBAction
	def removeVCallback_(self, sender):
		self.update()

	@objc.IBAction
	def removeHCallback_(self, sender):
		self.update()

	@objc.IBAction
	def removeICallback_(self, sender):
		self.update()

	@objc.python_method
	def rotation_transform(self, rotationCenter, rotationDegrees, direction):
		try:
			rotationX = rotationCenter.x
			rotationY = rotationCenter.y
			rotation = rotationDegrees * direction
			RotationTransform = NSAffineTransform.transform()
			RotationTransform.translateXBy_yBy_(rotationX, rotationY)
			RotationTransform.rotateByDegrees_(rotation)
			RotationTransform.translateXBy_yBy_(-rotationX, -rotationY)
			return RotationTransform
		except Exception as e:
			print(e)
			import traceback
			print(traceback.format_exc())

	@objc.python_method
	def get_center(self, layer):
		center = NSPoint(layer.bounds.origin.x + layer.bounds.size.width / 2, layer.bounds.origin.y + layer.bounds.size.height / 2)
		return center

	@objc.python_method
	def get_angle(self, node1, node2):
		myradians = atan2(node1.y - node2.y, node1.x - node2.x)
		return degrees(myradians)

	@objc.python_method
	def check_extreme_angle(self, layer, pathIdx, nodeIdx, pathTime, inputAngle):
		copy = layer.copy()
		path = copy.paths[pathIdx]
		path.insertNodeWithPathTime_(pathTime)
		newNode = path.nodes[nodeIdx]
		newOffcurve = path.nodes[nodeIdx - 1]
		angle = self.get_angle(newNode, newOffcurve)
		del copy
		if inputAngle - 1 <= abs(int(angle)) <= inputAngle + 1:
			return pathTime

	@objc.python_method
	def get_selection(self, layer):
		if layer.selectionBounds.origin.x > 10000000:
			return [n for p in layer.paths for n in p.nodes]
		else:
			return [n for p in layer.paths for n in p.nodes if n.selected]

	@objc.python_method
	def add_extremes(self, layer, addH=False):

		def get_pathTime_for_angle(layer, pathIdx, nodeIdx, pathTime, inputAngle):
			checkedPathtime = self.check_extreme_angle(layer, pathIdx, nodeIdx, pathTime, inputAngle)
			if checkedPathtime:
				path.insertNodeWithPathTime_(checkedPathtime)

		for i, path in enumerate(layer.paths):
			for idx in range(len(path.nodes) - 1, -1, -1):
				node = path.nodes[idx]
				if node in self.get_selection(layer) and path.nodes[idx - 3] in self.get_selection(layer) and node.type == "curve":
					p1 = path.nodes[idx - 3].position
					p2 = path.nodes[idx - 2].position
					p3 = path.nodes[idx - 1].position
					p4 = node.position
					allTs = TimesOfBezier(p1, p2, p3, p4, None, None, None, None)
					Ts = [x for x in allTs if x < 1]
					if len(Ts) > 0:
						pathTime = idx + Ts[0]
						get_pathTime_for_angle(layer, i, idx, pathTime, 90)
						if addH:
							get_pathTime_for_angle(layer, i, idx, pathTime, 0)
							get_pathTime_for_angle(layer, i, idx, pathTime, 180)

	@objc.python_method
	def delete_nodes(self, layer, inputAngle):
		for p in layer.paths:
			delete = []
			for n in p.nodes:
				prevDist = hypot(n.x - n.prevNode.x, n.y - n.prevNode.y)
				nextDist = hypot(n.x - n.nextNode.x, n.y - n.nextNode.y)
				if prevDist < nextDist:
					angle = self.get_angle(n, n.nextNode)
				elif nextDist < prevDist:
					angle = self.get_angle(n, n.prevNode)
				if n in self.get_selection(layer) and n.smooth and n.prevNode.type == n.nextNode.type == "offcurve" and n.type == "curve" and inputAngle - 1 <= abs(int(angle)) <= inputAngle + 1:
					delete.append(n)
			for d in delete:
				p.removeNodeCheckKeepShape_(d)

	@objc.python_method
	def filter(self, layer, inEditView, customParameters):

		if 'angles' in customParameters:
			angles = customParameters['angles']
		else:
			angles = Glyphs.defaults['com.joachimvu.ItalicExtremes.angles']

		if 'option' in customParameters:
			option = customParameters['option']
		else:
			option = Glyphs.defaults['com.joachimvu.ItalicExtremes.option']

		if 'removeV' in customParameters:
			removeV = customParameters['removeV']
		else:
			removeV = Glyphs.defaults['com.joachimvu.ItalicExtremes.removeV']

		if 'removeH' in customParameters:
			removeH = customParameters['removeH']
		else:
			removeH = Glyphs.defaults['com.joachimvu.ItalicExtremes.removeH']

		if 'removeI' in customParameters:
			removeI = customParameters['removeI']
		else:
			removeI = Glyphs.defaults['com.joachimvu.ItalicExtremes.removeI']

		angleList = [x.strip() for x in str(angles).split(",")]
		for a in angleList:
			try:
				italicAngle = float(a)
			except:
				pass
			if option == AddI:
				center = self.get_center(layer)
				rotate = self.rotation_transform(center, italicAngle, 1)
				rotateMatrix = rotate.transformStruct()
				layer.applyTransform(rotateMatrix)
				self.add_extremes(layer)
				rotate = self.rotation_transform(center, italicAngle, -1)
				rotateMatrix = rotate.transformStruct()
				layer.applyTransform(rotateMatrix)
				if removeV:
					self.delete_nodes(layer, 90)
				if removeH:
					self.delete_nodes(layer, 180)
					self.delete_nodes(layer, 0)
			elif option == AddHV:
				self.add_extremes(layer, addH=True)
				if removeI:
					self.delete_nodes(layer, 90 - italicAngle)
					self.delete_nodes(layer, 90 + italicAngle)

	@objc.python_method
	def generateCustomParameter(self):
		return "%s; angles:%s; option:%s; removeV:%s; removeH:%s; removeI:%s" % (
			self.__class__.__name__,
			Glyphs.defaults['com.joachimvu.ItalicExtremes.angles'],
			Glyphs.defaults['com.joachimvu.ItalicExtremes.option'],
			Glyphs.defaults['com.joachimvu.ItalicExtremes.removeV'],
			Glyphs.defaults['com.joachimvu.ItalicExtremes.removeH'],
			Glyphs.defaults['com.joachimvu.ItalicExtremes.removeI'],
		)

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__
