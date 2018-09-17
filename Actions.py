import win32api, win32con
import time
import json
import os
import os.path
import pyautogui
import random
import VirtualKeystroke
import tkinter as tk
import imagesearch as imgsearch
from ctypes import windll, Structure, c_long, byref
from abc import ABCMeta, abstractmethod
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.colorchooser import *
from PIL import Image, ImageTk
from Tools import KeyEntry
from Tools import NumberEntry
from Tools import TextEntry
from Tools import MouseOptionFrame
from Tools import ToggledFrame
from Tools import MouseScanFrame
from Tools import ScreenShot
from Tools import ToplevelObserver
from Tools import POINT
from Variables import VariableList
from Variables import VariableEditor


class Action():
	__metaclass__ = ABCMeta
	""" Actions that can be executed by the app """
	
	
	def __init__(self, actionType):
		self.delay = 0
		self.repeat = 1
		self.actionType = actionType
		self.dependentVars = []
		self.breakpoint = False
		
	
	def play(self):
		""" Do action unless there is a breakpoint, in which case pause the program """
		
		if self.breakpoint:
			return False
		else:
			return self.do_action()
		
		
	def is_playable(self, step):
		""" Check that the dependent variables exist so the action can run without error """
		
		for var in self.dependentVars:
			if not VariableList.contains(var):
				s = "Step " + str(step) + " missing variable " + str(var)
				messagebox.showinfo("Error", s)
				return False
		return True
			
			
	def do_action(self): raise NotImplementedError
	def display(self, master): raise NotImplementedError
	def save(self): raise NotImplementedError
	def load(self, data): raise NotImplementedError
	def get_data(self): raise NotImplementedError
	def quit(self): raise NotImplementedError
	def copy(self): raise NotImplementedError
	def enable_all(self): raise NotImplementedError
	def disable_all(self): raise NotImplementedError
		
		
class KeyAction(Action):
	__metaclass__ = ABCMeta
	""" Press a single key """
	
	def __init__(self, actionType):
		super(KeyAction, self).__init__(actionType)
		self.key = None
		
		
	def key_frame(self, menu):
		""" Returns a frame with a key entry """
		
		top = Frame(menu)
		
		top.columnconfigure(0, weight=1)
		top.columnconfigure(1, weight=1)
		top.rowconfigure(0, weight=1)
		
		Label(top, text="Key:").grid(row=0, column=0, sticky=(W))
		
		self.keyEntry = KeyEntry(top, 10)
		if(self.key is not None):
			self.keyEntry.insert(self.key)
		self.keyEntry.grid(row=0, column=1, sticky=(E))
		return top
	
		
	def copy(self, copy):
		""" Make a copy of the action and return it """
		
		copy.key = self.key
		copy.delay = self.delay
		copy.repeat = self.repeat
		return copy
		
		
	def save(self):
		""" Get data from the entries and save the values """
		
		self.key = self.keyEntry.get()
	
	
	def load(self, data):
		""" Load the data """
	
		self.delay = data['delay']
		self.repeat = data['repeat']
		self.key = data['key']
	
	
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		description = str(self.key)
		data = {
			'action': self.actionType,
			'delay': self.delay,
			'repeat': self.repeat,
			'key': self.key,
			'description': description}  
		return data
		
	def quit(self):
		return
	
	
		
class PressKey(KeyAction):
	__metaclass__ = ABCMeta
	""" Press a single key """
	
	def __init__(self):
		super(PressKey, self).__init__("Press Key")
		
	
	def display(self, menu):
		content = Frame(menu, width=150, height=30)
		content.grid_propagate(0)
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		
		keyFrame = self.key_frame(content)
		keyFrame.grid(row=0, column=0, sticky=(E,W))
		
		return content
		
		
	def do_action(self):
		""" Press key """
		
		if(self.key is not None):
			VirtualKeystroke.press(self.key)
		return True	
		
		
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = PressKey()
		copy = super(PressKey, self).copy(copy)
		return copy
		
		
		
class HoldKey(KeyAction):
	__metaclass__ = ABCMeta
	""" Hold a single key for some duration """
	
	def __init__(self):
		super(HoldKey, self).__init__("Hold Key")
		self.time = 0
	
	
	def display(self, menu):
		content = Frame(menu, width=150, height=60)
		content.grid_propagate(0)
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		
		keyFrame = self.key_frame(content)
		keyFrame.grid(row=0, column=0, pady=(0,5), sticky=(E,W))
		
		timeFrame = Frame(content)
		timeFrame.grid(row=1, column=0, sticky=(E,W))
		timeFrame.columnconfigure(0, weight=1)
		timeFrame.columnconfigure(1, weight=1)
		timeFrame.rowconfigure(0, weight=1)
		
		Label(timeFrame, text="Time(m/s):").grid(row=0, column=0, sticky=(W))
		self.timeEntry = NumberEntry(timeFrame, 9, 9, self.time)
		self.timeEntry.grid(row=0, column=1, sticky=(E))
		
		return content	
		
		
	def do_action(self):
		""" Hold key """
		
		if(self.key is not None):
			VirtualKeystroke.pressAndHold(self.time, self.key)
		return True
		
	
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = HoldKey()
		copy = super(HoldKey, self).copy(copy)
		copy.time = self.time
		return copy
		
		
	def save(self):
		""" Get data from the entries and save the values """
		
		super(HoldKey, self).save()
		self.time = self.timeEntry.get()
		
		
	def load(self, data):
		""" Load the data """
		
		super(HoldKey, self).load(data)
		self.time = data['time']
	
	
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		data = super(HoldKey, self).get_data()
		data['time'] = self.time
		return data
			
		
class WriteText(Action):
	__metaclass__ = ABCMeta
	""" Type up to 180 characters of text """
	
	def __init__(self):
		super(WriteText, self).__init__("Write Text")
		self.text = ''
		
		
	def display(self, menu):
		content = Frame(menu)
		
		content.columnconfigure(0, weight=0)
		content.columnconfigure(1, weight=0)
		content.rowconfigure(0, weight=1)
		
		lblTime = Label(content, text='Text:')
		lblTime.grid(row=0, column=0, padx=(0, 10), sticky=(W))
		
		self.textVal = TextEntry(content, 180, 25, 4, 'Max 180 chars')
		self.textVal.grid(row=0, column=1, sticky=(E))
		
		if(len(self.text) > 0):
			self.textVal.insert(self.text)
		
		return content
		
		
	def do_action(self):
		""" Type characters """
		
		VirtualKeystroke.typer(self.text)
		return True
		
		
	def save(self):
		""" Get data from the entries and save the values """
		
		self.text = self.textVal.get()
	
	
	def load(self, data):
		""" Load the data """
	
		self.delay = data['delay']
		self.repeat = data['repeat']
		self.text = data['text']
	
	
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		description = self.text
		data = {
			'action': self.actionType,
			'delay': self.delay,
			'repeat': self.repeat,
			'text': self.text,
			'description': description}  
		return data
	
	
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = WriteText()
		copy.text = self.text
		copy.delay = self.delay
		copy.repeat = self.repeat
		return copy
		
		
	def quit(self):
		return
		
		
class ClickMenu(Action):
	__metaclass__ = ABCMeta
	""" Display menu and common methoths for Left Click, Right Click, and Move Mouse actions """
	
	def __init__(self, actionType, label):
		super(ClickMenu, self).__init__(actionType)
		self.mousePos = POINT(0,0);
		self.label = label
		self.clickOption = StringVar()
		self.clickOption.set('Point')
		self.variables = StringVar()
		self.variables.set('None')
		self.randomness = 0
		
		
	def display(self, menu):
		content = Frame(menu, width=210, height=100)
		content.grid_propagate(0)
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		content.rowconfigure(2, weight=1)
		
		choices = ['Variable', 'Point']

		topFrame = Frame(content)
		topFrame.grid(row=0, column=0, pady=(0,5), sticky=(E, W))
		topFrame.columnconfigure(0, weight=1)
		topFrame.columnconfigure(1, weight=1)
		topFrame.rowconfigure(0, weight=1)
		
		Label(topFrame, text="Type:").grid(row=0, column=0, padx=(0,10), sticky=(W))
		
		clickChoice = Frame(topFrame, width=120, height=30)
		clickChoice.grid_propagate(0)
		clickChoice.columnconfigure(0, weight=1)
		clickChoice.rowconfigure(0, weight=1)
		clickOptionsMenu = OptionMenu(clickChoice, self.clickOption, *choices, command=self.change_click_option)
		clickOptionsMenu.grid(row=0, column=0, sticky=(N, S, E, W))
		clickChoice.grid(row=0, column=1, sticky=(E))

		
		self.optionFrame = Frame(content, width=210, height=30)
		self.optionFrame.grid_propagate(0)
		self.optionFrame.grid(row=1, column=0)
		
		middleFrame = Frame(content)
		middleFrame.grid(row=2, column=0, sticky=(E, W))
		middleFrame.columnconfigure(0, weight=1)
		middleFrame.columnconfigure(1, weight=1)
		middleFrame.rowconfigure(0, weight=1)
		
		Label(middleFrame, text="Add Randomness:").grid(row=0, column=0, padx=(0,5), sticky=(W))
		self.randomnessEntry = NumberEntry(middleFrame, 9, 9, '0')
		self.randomnessEntry.grid(row=0, column=1, sticky=(E))
		self.randomnessEntry.insert(self.randomness)
		
		self.change_click_option()
		return content
		
		
	def change_click_option(self, *args):
		""" Change the click option frame display whenever the option is changed """
		
		for widget in self.optionFrame.winfo_children():
			widget.destroy()
		
		if(self.clickOption.get() == 'Variable'):
			self.optionFrame.columnconfigure(0, weight=1)
			self.optionFrame.columnconfigure(1, weight=0)
			self.optionFrame.columnconfigure(2, weight=0)
			self.optionFrame.rowconfigure(0, weight=1)
			
			choices = list(VariableList.vars.keys())
			if len(choices) < 1:
				choices = ['None']
			
			lblV = Label(self.optionFrame, text='Variable:')
			lblV.grid(row=0, column=0, padx=(0,10), sticky=(W))
			
			varChoice = Frame(self.optionFrame, width=120, height=30)
			varChoice.grid_propagate(0)
			varChoice.columnconfigure(0, weight=1)
			varChoice.rowconfigure(0, weight=1)
			variableOptionsMenu = OptionMenu(varChoice, self.variables, *choices)
			variableOptionsMenu.grid(row=0, column=0, sticky=(N, S, E, W))
			varChoice.grid(row=0, column=1, sticky=(E))
			
			add = Button(self.optionFrame, text="+", command=self.edit_variables)
			add.grid(row=0, column=2, sticky=(E))
			
				
		else:
			self.optionFrame.columnconfigure(0, weight=1)
			self.optionFrame.columnconfigure(1, weight=1)
			self.optionFrame.rowconfigure(0, weight=1)
			
			Label(self.optionFrame, text="Location:").grid(row=0, column=0, sticky=(W))
			
			self.mouseOpFrame = MouseOptionFrame(self.optionFrame, self.mousePos)
			self.mouseOpFrame.grid(row=0, column=1, sticky=(E))
		
	
	def get_point(self):
		""" Get the point location of the click with the added randomness """
		
		x = 0
		y = 0
		if(self.clickOption.get() == 'Point'):
			x = int(self.mousePos.x)
			y = int(self.mousePos.y)
		else:
			pt = VariableList.get(self.variables.get()).get()
			x = pt.x
			y = pt.y
			
		rand = random.randint(0, self.randomness)
		xvec = random.uniform(0, 1)
		yvec = 1.0 - xvec
		
		randx = xvec * rand
		randy = yvec * rand
		
		if random.randint(0, 1):
			randx = randx * -1
		
		if random.randint(0, 1):
			randy = randy * -1
			
		x = int(x + randx)
		y = int(y + randy)
		return POINT(x,y)
		
			
	def edit_variables(self):
		""" Open the variale editor """
		
		editor = VariableEditor()
		editor.action = self
		
	
	def save(self):
		""" Get data from the entries and save the values """
		
		if self.clickOption.get() == 'Point':
			self.mousePos = self.mouseOpFrame.get()
		self.randomness = self.randomnessEntry.get()
		
		
	def load(self, data):
		""" Load the data """
		
		self.delay = data['delay']
		self.repeat = data['repeat']
		self.mousePos = POINT(data['mouse position x'], data['mouse position y'])
		self.clickOption.set(data['click option'])
		self.variables.set(data['variable'])
		self.randomness = data['randomness']
		
		
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		description = '(' + str(self.mousePos.x) + ', ' + str(self.mousePos.y) + ')'
		data = {
			'action': self.actionType,
			'delay': self.delay,
			'repeat': self.repeat,
			'click option': self.clickOption.get(),
			'variable': self.variables.get(),
			'mouse position x': self.mousePos.x,
			'mouse position y': self.mousePos.y,
			'randomness': self.randomness,
			'description': description}  
		return data
		
		
	def quit(self):
		return
		
		
	def do_action(self): raise NotImplementedError
	def copy(self): raise NotImplementedError
	
	
class LeftClick(ClickMenu):
	""" Left Click at specified screen position """
	
	def __init__(self):
		super(LeftClick, self).__init__('Left Click', 'Left Click At:')
		
		
	def do_action(self):
		""" Left Click """
		
		pt = self.get_point()
		win32api.SetCursorPos((pt.x,pt.y))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,pt.x,pt.y,0,0)
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,pt.x,pt.y,0,0)
		return True
			
			
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = LeftClick()
		copy.mousePos = self.mousePos
		copy.delay = self.delay
		copy.repeat = self.repeat
		copy.clickOption = self.clickOption
		copy.variables = self.variables
		copy.randomness = self.randomness
		return copy
	
	
class RightClick(ClickMenu):
	""" Right Click at specified screen position """
	
	def __init__(self):
		super(RightClick, self).__init__('Right Click', 'Right Click At:')
		
		
	def do_action(self):
		""" Right Click """
		
		pt = self.get_point()
		win32api.SetCursorPos((pt.x,pt.y))
		win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,pt.x,pt.y,0,0)
		win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,pt.x,pt.y,0,0)
		return True
			
			
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = RightClick()
		copy.mousePos = self.mousePos
		copy.delay = self.delay
		copy.repeat = self.repeat
		copy.clickOption = self.clickOption
		copy.variables = self.variables
		copy.randomness = self.randomness
		return copy
	
	
class MoveMouse(ClickMenu):
	""" Move mouse to specified screen position """

	def __init__(self):
		super(MoveMouse, self).__init__('Mouse Move', 'Move Mouse To:')
		
	def do_action(self):
		""" Move mouse """
		
		pt = self.get_point()
		win32api.SetCursorPos((pt.x,pt.y))
		return True
			
			
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = MoveMouse()
		copy.mousePos = self.mousePos
		copy.delay = self.delay
		copy.repeat = self.repeat
		copy.clickOption = self.clickOption
		copy.variables = self.variables
		copy.randomness = self.randomness
		return copy
	
		
class DetectImage(Action):
	""" Detect an image and store it's screen position in a variable """
	
	def __init__(self):
		super(DetectImage, self).__init__('Detect Image')
		self.scanPoint = POINT(0,0);
		self.scanWidth = 0
		self.scanHeight = 0
		self.retryTimer = 0
		self.precision = 0
		self.failDefaultValue = POINT(0,0);
		self.screenshot = None
		self.storeVariable = StringVar()
		self.storeVariable.set('None')
		self.failOption = StringVar()
		self.failOption.set('Stop Program')
		
		
	def display(self, master):
		content = Frame(master)
		self.master = master
		
		content.columnconfigure(0, weight=0)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		
		# Top frame
		
		top = Frame(content)
		top.grid(row=0, column=0, sticky=(N,W))
		
	
		top.columnconfigure(0, weight=1)
		top.columnconfigure(1, weight=1)
		top.rowconfigure(0, weight=1)

		# Scan options on the left
		
		left = Frame(top)
		left.grid(row=0, column=0, sticky=(N,S,W))
		left.columnconfigure(0, weight=1)
		left.rowconfigure(0, weight=1)
		
		borderFrame = Frame(left, relief=GROOVE, borderwidth=2)
		borderFrame.grid(row=0, column=0, pady= (10, 0), sticky=(N,S,E,W))
		
		borderFrame.columnconfigure(0, weight=1)
		borderFrame.rowconfigure(0, weight=0)
		borderFrame.rowconfigure(1, weight=1)
		
		Label(left, text='Scan Area').place(relx=.08, rely=0.08,anchor=W)
		
		
		self.scanPointFrame = MouseScanFrame(borderFrame)
		self.scanPointFrame.grid(row=0, column=0, sticky=(N, W), pady=(15,0), padx = 15)
		self.scanPointFrame.set([self.scanPoint.x, self.scanPoint.y, self.scanWidth, self.scanHeight])
		
		precisionFrame = Frame(borderFrame)
		precisionFrame.grid(row=1, column=0, sticky=(N, W), padx = 15, pady = (10,0))
		
		precisionFrame.columnconfigure(0, weight=1)
		precisionFrame.columnconfigure(1, weight=1)
		precisionFrame.rowconfigure(0, weight=1)
		
		
		Label(precisionFrame, text='Precision:').grid(row=0, column=0, padx=(0, 5), sticky=(N,W))
		
		self.precisonScale = Scale(precisionFrame, from_=0, to=100, orient=HORIZONTAL)
		self.precisonScale.grid(row=0, column=1)
		self.precisonScale.set(self.precision)
		
		
		# Image and screenshot on the right
		
		right = Frame(top)
		right.grid(row=0, column=1, sticky=(N,S,W))
		right.columnconfigure(0, weight=1)
		right.rowconfigure(0, weight=1)
			
		
		
		ImageBorder = Frame(right, relief=GROOVE, borderwidth=2)
		ImageBorder.grid(row=0, column=1, sticky=(N,S,E,W), pady= (10, 0))
		
		ImageBorder.columnconfigure(0, weight=1)
		ImageBorder.rowconfigure(0, weight=1)

		Label(right, text='For Image').place(relx=.08, rely=0.08,anchor=W)
		
		ImageFrame = Frame(ImageBorder)
		ImageFrame.grid(row=0, column=0, padx = 15, pady = 15, sticky=(N,S))
		
		ImageFrame.columnconfigure(0, weight=1)
		ImageFrame.rowconfigure(0, weight=1)
		ImageFrame.rowconfigure(1, weight=1)
		
		pathFrame = Frame(ImageFrame)
		pathFrame.grid(row=0, column=0, sticky=(N,W))
		
		pathFrame.columnconfigure(0, weight=1)
		pathFrame.columnconfigure(1, weight=1)
		pathFrame.columnconfigure(2, weight=1)
		pathFrame.rowconfigure(0, weight=1)
		
		
		
		self.imgLabel = Label(pathFrame, text='Image', width=15, height=1)
		self.imgLabel.grid(row=0, column=0, padx=(0,5))
		Button(pathFrame, text="Open", command=self.open_img).grid(row=0, column=1, padx=(0,5))
		Button(pathFrame, text="Screenshot", command=self.open_screenshot).grid(row=0, column=2, sticky=(W))
		
		imgBorder = Frame(ImageFrame, width=85, height=85)
		imgBorder.grid(row=1, column=0, sticky=(N,W), pady=(10,0))
		
		imgBorder.columnconfigure(0, weight=1)
		imgBorder.rowconfigure(0, weight=1)
		
		imgBorder.grid_propagate(0)
		
		self.imgDisplay = Label(imgBorder)
		self.imgDisplay.grid(row=1, column=0, sticky=(N,S,E, W))
		
		
		if(self.screenshot is not None):
			shortPath =  ('...' + self.screenshot[-15:]) if len(self.screenshot) > 15 else ('...' + self.screenshot)
			self.imgLabel.configure(text=shortPath)
			self.display_img(self.screenshot)
		
		
		# Options frame at the bottom
		
		optionFrame = Frame(content, width=250, height=100)
		optionFrame.grid_propagate(0)
		optionFrame.grid(row=1, column=0, pady=(10,0), sticky=(N, W))
		
		optionFrame.columnconfigure(0, weight=1)
		optionFrame.columnconfigure(1, weight=1)
		optionFrame.columnconfigure(2, weight=1)
		optionFrame.rowconfigure(0, weight=0)
		optionFrame.rowconfigure(1, weight=0)
		optionFrame.rowconfigure(2, weight=1)
		
		
		choices = ['None']
		
		lblV = Label(optionFrame, text='Store in variable:')
		lblV.grid(row=0, column=0, padx=(0,10), pady=(0,5), sticky=(W))
		
		varChoice = Frame(optionFrame, width=120, height=30)
		varChoice.grid_propagate(0)
		varChoice.columnconfigure(0, weight=1)
		varChoice.rowconfigure(0, weight=1)
		self.variableOptions = OptionMenu(varChoice, self.storeVariable, *choices)
		self.variableOptions.grid(row=0, column=0, sticky=(N, S, E, W))
		varChoice.grid(row=0, column=1, padx=(0,5), sticky=(E))
		
		add = Button(optionFrame, text="+", command=self.edit_variables)
		add.grid(row=0, column=2, sticky=(E))
		
		
		choices = ['Stop Program', 'Set Default Value', 'Retry']
		
		lblF = Label(optionFrame, text='If fails:')
		lblF.grid(row=1, column=0, padx=(0,10), pady=(0,5), sticky=(W))
		
		failChoice = Frame(optionFrame, width=160, height=30)
		failChoice.grid_propagate(0)
		failChoice.columnconfigure(0, weight=1)
		failChoice.rowconfigure(0, weight=1)
		self.failOptionMenu = OptionMenu(failChoice, self.failOption, *choices)
		self.failOptionMenu.grid(row=0, column=0, sticky=(N, S, E, W))
		failChoice.grid(row=1, column=1, columnspan=2, sticky=(E))
		
		
		self.lbl1 = Label(optionFrame, text='Screen Point:')
		self.mouseOpFrame = MouseOptionFrame(optionFrame, self.failDefaultValue)
		
		self.lbl2 = Label(optionFrame, text='Retry for(ms):')
		self.retryTimerEntry = NumberEntry(optionFrame, 8, 8, str(self.retryTimer))
		
		self.failOption.trace("w", self.change_fail_option)
		
		self.change_fail_option()
		self.refresh_variable_options()
		
		return content
		
		
	def do_action(self):
		""" Scan a specified area of the screen for an image and store the location in a variable """
		
		try:
			img = Image.open(self.screenshot)
		except:
			if(self.screenshot is None):
				s = "No image selected in detect image action"
			else:
				s = "Image " + self.screenshot + " Not Found."
			messagebox.showinfo("Image Not Found", s, parent=ToplevelObserver.top())
			return False
			
		width, height = img.size
		pt = imgsearch.imagesearcharea(self.screenshot, self.scanPoint.x, self.scanPoint.y, self.scanPoint.x + self.scanWidth, self.scanPoint.y + self.scanHeight, precision=(float(self.precision)/100.0))
		point = POINT(int(pt[0] + (width/2) + self.scanPoint.x), int(pt[1] + (height/2 + self.scanPoint.y)))
		if(pt[0] is -1):
			if (self.failOption.get() == 'Set Default Value'):
				point = self.failDefaultValue
			elif (self.failOption.get() == 'Retry'):
				while(pt[0] is -1):
					pt = imgsearch.imagesearcharea(self.screenshot, self.scanPoint.x, self.scanPoint.y, self.scanPoint.x + self.scanWidth, self.scanPoint.y + self.scanHeight, precision=(float(self.precision)/100.0))
				point = POINT(int(pt[0] + (width/2) + self.scanPoint.x), int(pt[1] + (height/2 + self.scanPoint.y)))
			else:
				s = "Image not found, stopping."
				messagebox.showinfo("Image Not Found", s, parent=ToplevelObserver.top())
				return False
				
		s = str(point.x) + " " + str(point.y)
		VariableList.set(self.storeVariable.get(), point)
		return True
		
		
	def refresh_variable_options(self):
		""" Change the variable options available when a variable is added to or removed from the variable list """
		
		choices = list(VariableList.vars.keys())
		if not (self.storeVariable.get() in choices):
			self.storeVariable.set('None')
		
		menu = self.variableOptions['menu']
		menu.delete(0, 'end')
		
		if len(choices) > 0:
			for choice in choices:
				# Add menu items.
				menu.add_command(label=choice, command=tk._setit(self.storeVariable, choice))
			self.variableOptions.configure(state="normal")
			
		else:
			self.variableOptions.configure(state="disabled")
			
			
	def change_fail_option(self, *args):
		""" Change the display of the fail option frame when the value of the fail optio is changed """
		
		if (self.failOption.get() == 'Set Default Value'):
			self.lbl2.grid_forget()
			self.retryTimerEntry.grid_forget()
			
			self.lbl1.grid(row=2, column=0, sticky=(W), padx=(0, 5))
			self.mouseOpFrame.grid(row=2, column=1, sticky=(W))
			
		elif (self.failOption.get() == 'Retry'):
			self.lbl1.grid_forget()
			self.mouseOpFrame.grid_forget()
			
			self.lbl2.grid(row=2, column=0, sticky=(W), padx=(0, 5))
			self.retryTimerEntry.grid(row=2, column=1, sticky=(W))
		else:
			self.lbl2.grid_forget()
			self.retryTimerEntry.grid_forget()
			self.lbl1.grid_forget()
			self.mouseOpFrame.grid_forget()
			
		
	def edit_variables(self):
		""" Open the variable editor """
		
		editor = VariableEditor()
		editor.action = self
		
			
	def open_img(self):
		""" Open and display an image """
		
		path = "Images"
		filename = filedialog.askopenfilename(parent=self.master, initialdir = path, filetypes = (("png files","*.png"),("all files","*.*")))
		if os.path.isfile(filename):
			self.screenshot = filename
			shortPath =  ('...' + filename[-15:]) if len(filename) > 15 else ('...' + filename)
			self.imgLabel.config(text=shortPath)
			self.display_img(filename)
		else:
			print("No file exists")
			
	
	def display_img(self, path):
		""" Display image and resize to fit the right frame """
	
		img = Image.open(path)
		width, height = img.size
		
		maxSize = 80
		
		if width > 0 and height > 0:
			if width > height:
				p = float(maxSize)/float(width)
				width = maxSize
				height = int(float(height) * p)
			else:
				p = float(maxSize)/float(height)
				height = maxSize
				width = int(float(width) * p)
			
			
			resized = img.resize((width, height), Image.ANTIALIAS)
			
			temp = ImageTk.PhotoImage(resized)
			
			self.imgDisplay.configure(image=temp)
			self.imgDisplay.image = temp
			
	
	def open_screenshot(self):
		""" Open screenshot window """
		
		ScreenShot(self)
		
		
	def save(self):
		""" Get data from the entries and save the values """
		
		scan = self.scanPointFrame.get()
		self.scanPoint = POINT(scan[0], scan[1])
		self.scanWidth = scan[2]
		self.scanHeight = scan[3]
		
		self.dependentVars = [self.storeVariable.get()]
		self.precision = self.precisonScale.get()
		
		if (self.failOption.get() == 'Set Default Value'):
			self.failDefaultValue = self.mouseOpFrame.get()
			
		elif (self.failOption.get() == 'Retry'):
			self.retryTimer = self.retryTimerEntry.get()
		
	
	def load(self, data):
		""" Load the data """
		
		self.delay = data['delay']
		self.repeat = data['repeat']
		self.scanPoint = POINT(data['scan point x'], data['scan point y'])
		self.scanWidth = data['scan width']
		self.scanHeight = data['scan height']
		self.failDefaultValue = POINT(data['fail default x'], data['fail default y'])
		self.screenshot = data['screenshot']
		self.storeVariable.set(data['store variable'])
		self.failOption.set(data['fail option'])
		self.precision = data['precision']
		self.dependentVars = [data['store variable']]
		
	
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		description = self.screenshot
		data = {
			'action': self.actionType,
			'delay': self.delay,
			'repeat': self.repeat,
			'scan point x': self.scanPoint.x,
			'scan point y': self.scanPoint.y,
			'scan width': self.scanWidth,
			'scan height': self.scanHeight,
			'fail default x': self.failDefaultValue.x,
			'fail default y': self.failDefaultValue.y,
			'screenshot': self.screenshot,
			'store variable': self.storeVariable.get(),
			'fail option': self.failOption.get(),
			'precision': self.precision,
			'description': description}  
		return data
		
		
	def copy(self):
		""" Make a copy of the action and return it """
		
		copy = DetectImage()
		copy.scanPoint = self.scanPoint
		copy.scanWidth = self.scanWidth
		copy.scanHeight = self.scanHeight
		copy.failDefaultValue = self.failDefaultValue
		copy.retryTimer = self.retryTimer
		copy.screenshot = self.screenshot
		copy.storeVariable = self.storeVariable
		copy.failOption = self.failOption
		copy.precision = self.precision
		copy.delay = self.delay
		copy.repeat = self.repeat
		copy.dependentVars = self.dependentVars.copy()
		return copy
		
		
	def quit(self):
		for ti in self.failOption.trace_vinfo():
			self.failOption.trace_vdelete(*ti)
		return

	
class OpenAction(Toplevel):
	""" Open and display an action to edit """
	
	def __init__(self, action, tree, iid):
		Toplevel.__init__(self)
		self.protocol("WM_DELETE_WINDOW", self.quit)
		self.attributes('-topmost', 'true')
		self.grab_set()
		self.action = action
		self.loopType = StringVar()
		self.tree = tree
		self.iid = iid
		top = ToplevelObserver.top()
		loc = '+' + str(top.winfo_x()) + '+' + str(top.winfo_y())
		self.geometry(loc)
		
		
		self.winfo_toplevel().minsize(250, 100)
		self.resizable(False, False)
		self.wm_title(action.actionType)
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		content = Frame(self)
		content.grid(row=0, column=0, padx = 10, pady = 10, sticky=(N, S, E, W))
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		
		
		#Action
		
		self.actionFrame = self.action.display(content)
		
		self.actionFrame.columnconfigure(0, weight=1)
		self.actionFrame.rowconfigure(0, weight=1)
		
		self.actionFrame.grid(row=0, column=0, pady=(0,5), sticky=(N, W))
		
		
		optionsFrame =  Frame(content)
		optionsFrame.grid(row=1, column=0, sticky=(S, E))
		
		optionsFrame.columnconfigure(0, weight=1)
		optionsFrame.columnconfigure(1, weight=1)
		optionsFrame.rowconfigure(0, weight=1)
		
		acceptFrame = Frame(optionsFrame, width=50, height=25)
		acceptFrame.grid(row=0, column=0, sticky=(E), padx = (0,5))
		acceptFrame.grid_propagate(0)
		acceptFrame.columnconfigure(0, weight=1)
		acceptFrame.rowconfigure(0, weight=1)
		self.acceptButton = Button(acceptFrame, text="Accept", command=self.accept)
		self.acceptButton.grid(row=0, column=0, sticky=(N, S, E, W))

		cancelFrame = Frame(optionsFrame, width=50, height=25)
		cancelFrame.grid(row=0, column=1, sticky=(E))
		cancelFrame.grid_propagate(0)
		cancelFrame.columnconfigure(0, weight=1)
		cancelFrame.rowconfigure(0, weight=1)
		cancel = Button(cancelFrame, text="Cancel", command=self.quit)
		cancel.grid(row=0, column=0, sticky=(N, S, E, W))
		
		ToplevelObserver.add_element(self)
		
	
	def disable_all(self):
		""" Disable accepting action changes when the program is playing """
		
		self.acceptButton['state'] = 'disabled'
	
	
	def enable_all(self):
		""" Re-enable accepting action changes when program is stopped """
		
		self.acceptButton['state'] = 'normal'
	
	
	def accept(self, *args):
		""" Accept changes and save the action """
		
		self.action.save()
		self.iid = self.tree.save_action(self.action, self.iid)
		self.quit()
		
	def quit(self, *args):
		self.action.quit()
		ToplevelObserver.remove_element(self)
		self.destroy()
		