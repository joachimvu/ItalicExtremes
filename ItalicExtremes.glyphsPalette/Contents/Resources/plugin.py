# encoding: utf-8

###########################################################################################################
#
#
# Palette Plugin
#
# Read the docs:
# https://github.com/schriftgestalt/GlyphsSDK/tree/master/Python%20Templates/Palette
#
#
###########################################################################################################
from __future__ import division, print_function
from AppKit import NSBundle
from GlyphsApp import *
from GlyphsApp.plugins import *
from Foundation import NSPoint, NSAffineTransform, NSAffineTransformStruct
from vanilla import *
from math import atan2, degrees, hypot
from vanilla import *

bundle = NSBundle.bundleForClass_(GSFont.__class__)
objc.initFrameworkWrapper("GlyphsCore",
	frameworkIdentifier="com.schriftgestaltung.GlyphsCore",
	frameworkPath=bundle.bundlePath(),
	globals=globals())

class ItalicExtremes (PalettePlugin):

	def settings(self):
		self.name = "Italic Extremes"
		windowWidth  = 160
		windowHeight = 130
		m, h, yPos = 10, 18, 10
		self.w = Window(( windowWidth, windowHeight ))
		self.w.group = Group((0, 0, windowWidth, windowHeight))
		self.w.group.angle = EditText( (m, yPos, -m, h), Glyphs.font.selectedFontMaster.italicAngle, placeholder='Angle', sizeStyle='small')
		yPos += m+h
		self.w.group.italicButton = Button( (m, yPos, -m, h), "Add slanted nodes", sizeStyle='small', callback=self.italic_ )
		yPos += h
		self.w.group.removeV = CheckBox((m, yPos, -m, h), "Delete vertical extremes", sizeStyle='mini', value= True)
		yPos += 5+h
		self.w.group.sep = HorizontalLine((m, yPos, -m, 1))
		yPos += m
		self.w.group.verticalButton = Button( (m, yPos, -m, h), "Add  vertical extremes", sizeStyle='small', callback=self.vertical_ )
		yPos += h
		self.w.group.removeI = CheckBox((m, yPos, -m, h), "Delete slanted nodes", sizeStyle='mini', value= True)

		self.dialog = self.w.group.getNSView()

	def __del__(self):
			Glyphs.removeCallback(self.italic)
			Glyphs.removeCallback(self.vertical)

	@objc.python_method
	def rotation_transform( self, rotationCenter, rotationDegrees, direction ):
		try:
			rotationX = rotationCenter.x
			rotationY = rotationCenter.y
			rotation  = rotationDegrees * direction
			RotationTransform = NSAffineTransform.transform()
			RotationTransform.translateXBy_yBy_( rotationX, rotationY )
			RotationTransform.rotateByDegrees_( rotation )
			RotationTransform.translateXBy_yBy_( -rotationX, -rotationY )
			return RotationTransform
		except Exception as e:
			import traceback
			print(traceback.format_exc())

	@objc.python_method
	def get_center( self, layer ):
		center = NSPoint( layer.bounds.origin.x + layer.bounds.size.width/2, layer.bounds.origin.y + layer.bounds.size.height/2 )
		return center

	@objc.python_method
	def get_angle(self, node1, node2):
		myradians = atan2(node1.y-node2.y, node1.x-node2.x)
		return degrees(myradians)

	@objc.python_method
	def check_extreme_angle(self, layer, pathIdx, nodeIdx, pathTime):
		copy = layer.copy()
		path = copy.paths[pathIdx]
		path.insertNodeWithPathTime_(pathTime)
		newNode = path.nodes[nodeIdx]
		newOffcurve = path.nodes[nodeIdx - 1]
		angle = self.get_angle(newNode, newOffcurve)
		del copy
		if 89 <= abs(int(angle)) <= 91:
			return pathTime

	@objc.python_method
	def get_selection(self, layer):
		if "%s"%layer.selectionBounds.origin.x == "9.22337203685e+18":
			return [n for p in layer.paths for n in p.nodes]
		else:
			return [n for p in layer.paths for n in p.nodes if n.selected]

	@objc.python_method
	def add_extremes(self, layer):
		for i,path in enumerate(layer.paths):
			for idx in range(len(path.nodes) -1, -1, -1):
				node = path.nodes[idx]
				if node in self.get_selection(layer) and path.nodes[idx - 3] in self.get_selection(layer) and node.type == "curve":
					p1 = path.nodes[idx - 3].position
					p2 = path.nodes[idx - 2].position
					p3 = path.nodes[idx - 1].position
					p4 = node.position
					allTs = GSExtremTimesOfBezier(p1, p2, p3, p4, None, None, None, None)
					Ts = [x for x in allTs if x < 1]
					if len(Ts) > 0:
						pathTime = idx + Ts[0]
						checkedPathtime = self.check_extreme_angle(layer, i, idx, pathTime)
						if checkedPathtime:
							path.insertNodeWithPathTime_(checkedPathtime)

	@objc.python_method
	def delete_nodes(self, layer, angleType):
		for p in layer.paths:
			delete = []
			for n in p.nodes:
				prevDist = math.hypot(n.x - n.prevNode.x, n.y - n.prevNode.y)
				nextDist = math.hypot(n.x - n.nextNode.x, n.y - n.nextNode.y)
				if prevDist < nextDist:
					angle = self.get_angle(n, n.nextNode)
				elif nextDist < prevDist:
					angle = self.get_angle(n, n.prevNode)
				if n in self.get_selection(layer) and n.smooth and n.prevNode.type == n.nextNode.type == "offcurve" and n.type == "curve" and angleType-1 <= abs(int(angle)) <= angleType+1 :
					print(n)
					delete.append(n)
			for d in delete:
				p.removeNodeCheckKeepShape_(d)

	def italic_( self, sender):
		try:
			italicAngle = float(self.w.group.angle.get())
			for l in Glyphs.font.selectedLayers:
				center = self.get_center(l)
				rotate = self.rotation_transform( center, italicAngle, 1 )
				rotateMatrix = rotate.transformStruct()
				l.applyTransform(rotateMatrix)
				self.add_extremes(l)
				rotate = self.rotation_transform( center, italicAngle, -1 )
				rotateMatrix = rotate.transformStruct()
				l.applyTransform(rotateMatrix)
				if self.w.group.removeV.get():
					self.delete_nodes(l, 90)
		except Exception as e:
			import traceback
			print(traceback.format_exc())

	def vertical_(self, sender):
		try:
			italicAngle = float(self.w.group.angle.get())
			for l in Glyphs.font.selectedLayers:
				self.add_extremes(l)
				if self.w.group.removeI.get():
					self.delete_nodes(l, 90-italicAngle)
					self.delete_nodes(l, 90+italicAngle)
		except Exception as e:
			import traceback
			print(traceback.format_exc())

	@objc.python_method
	def __file__(self):
		"""Please leave this method unchanged"""
		return __file__