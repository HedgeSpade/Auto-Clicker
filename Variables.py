import win32api, win32con
import time
import json
import os
import os.path
import pyautogui
import VirtualKeystroke
from ctypes import windll, Structure, c_long, byref
from abc import ABCMeta, abstractmethod
from imagesearch import *
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


class Variable():
	__metaclass__ = ABCMeta
	""" A variable can have data stored in them from actions and then used later """
	
	def __init__(self, variableType, name):
		self.variableType = variableType
		self.name = name
		
			
	def display(self, master): raise NotImplementedError
	def get(self): raise NotImplementedError
	def save(self): raise NotImplementedError
	def load(self, data): raise NotImplementedError
	def get_data(self): raise NotImplementedError
	def copy(self): raise NotImplementedError
		

class PointVariable(Variable):
	""" Variable that holds a point value """
	
	def __init__(self, name):
		super(PointVariable, self).__init__("Point", name)
		self.value = POINT(0,0)
		
		
	def display(self, master):
		content = Frame(master)
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		
		frame = Frame(content)
		
		frame.columnconfigure(0, weight=1)
		frame.rowconfigure(0, weight=0)
		frame.grid(row=0, column=0, sticky=(N,W))
		
		
		stringFrame = Frame(frame)
		stringFrame.columnconfigure(0, weight=1)
		stringFrame.columnconfigure(1, weight=1)
		stringFrame.rowconfigure(0, weight=0)
		stringFrame.rowconfigure(1, weight=0)
		stringFrame.grid(row=0, column=0, sticky=(W))
		
		nameLbl = Label(stringFrame, text='Name:')
		nameLbl.grid(row=0, column=0, sticky=(W), padx = 10, pady = (0,5))
		
		self.varNameEntry = Entry(stringFrame, width=12)
		self.varNameEntry.grid(row=0, column=1, sticky=(W))
		
		self.varNameEntry.insert(0, self.name)
		
		varStringLbl = Label(stringFrame, text='Value:')
		varStringLbl.grid(row=1, column=0, sticky=(W), padx = 10)
		
		self.mouseOp = MouseOptionFrame(stringFrame, self.value)
		self.mouseOp.grid(row=1, column=1, sticky=(W))

		return content
		
		
	def get(self):
		""" Return the value of the point variable """
		
		return self.value
		
		
	def set(self, point):
		""" Set the value of the point variable """
		
		self.value = point
	
	
	def save(self):
		""" Get data from the entries and save the values """
		
		self.value = self.mouseOp.get()
		self.name = self.varNameEntry.get()
		
	
	def load(self, data):
		""" Load the data """
		
		self.value = POINT(data['value x'], data['value y'])
		
	
	def get_data(self):
		""" Build and return a packet of info to save in a .json """
		
		description = '(' + str(self.value.x) + ', ' + str(self.value.y) + ')' 
		data = {
			'name':self.name,
			'type': self.variableType,
			'description': description,
			'value x': self.value.x,
			'value y': self.value.y} 
		return data
	
	
	def copy(self):
		""" Make a copy of the variable and return it """
		
		copy = PointVariable(self.name)
		copy.value = self.value
		return copy
		
		
class VariableEditor(Toplevel):
	""" Variable editor window that displays a tree of all variables """
	
	def __init__(self):
		Toplevel.__init__(self)
		self.protocol("WM_DELETE_WINDOW", self.quit)
		self.attributes('-topmost', 'true')
		self.grab_set()
		self.winfo_toplevel().minsize(200, 100)
		self.resizable(False, False)
		self.wm_title("Variable Editor")
		
		VariableList.editor = self
		
		self.treeItems = {}
		self.running = False
		self._add = None
		self._delete = None
		self._edit = None
		self.tree = None
		self.action = None
		
		content = Frame(self)
		content.grid(row=0, column=0, sticky=(N, S, E, W))
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)

	
		#Top
	
		topFrame = Frame(content)
		topFrame.grid(row=0, column=0, sticky=(N, S, E, W))
		
		topFrame.columnconfigure(0, weight=1)
		topFrame.rowconfigure(0, weight=1)
		
		border = Frame(topFrame)
		border.grid(row=0, column=0, padx = 10, pady = 10, sticky=(N, S, E, W))
		
		border.columnconfigure(0, weight=1)
		border.columnconfigure(1, weight=1)
		border.rowconfigure(0, weight=1)
		border.rowconfigure(1, weight=1)
		
		self.variableType = StringVar()
		choices = [ 'Point']
		self.variableType.set('Point')
		
		
		variableChoiceFrame = Frame(border)
		
		variableChoiceFrame.columnconfigure(0, weight=0)
		variableChoiceFrame.columnconfigure(1, weight=1)
		variableChoiceFrame.columnconfigure(2, weight=1)
		variableChoiceFrame.rowconfigure(0, weight=1)
		
		lblV = Label(variableChoiceFrame, text='Variable:')
		lblV.grid(row=0, column=0, padx=(0,10), sticky=(W))
		
		varChoice = Frame(variableChoiceFrame, width=120, height=30)
		varChoice.grid_propagate(0)
		varChoice.columnconfigure(0, weight=1)
		varChoice.rowconfigure(0, weight=1)
		variable = OptionMenu(varChoice, self.variableType, *choices)
		variable.grid(row=0, column=0, sticky=(N, S, E, W))
		varChoice.grid(row=0, column=1, sticky=(E))
		
		self.nameEntry = Entry(variableChoiceFrame)
		self.nameEntry.grid(row=0, column=2, sticky=(E))
		
		variableChoiceFrame.grid(row=0, column=0, sticky=(N, E, W))
		
		treeBorderFrame = Frame(border, relief="ridge", borderwidth=2)
		treeBorderFrame.grid(row=1, column=0, sticky=(N, S, E, W))
		
		treeBorderFrame.columnconfigure(0, weight=1)
		treeBorderFrame.rowconfigure(0, weight=1)
		
		treeFrame = Frame(treeBorderFrame)
		treeFrame.pack(side=TOP, fill=BOTH, expand=Y)
		
		treeFrame.rowconfigure(0, weight=1)
		treeFrame.columnconfigure(0, weight=1)
		treeFrame.columnconfigure(1, weight=0)
		
		
		# create the tree and scrollbars
		dataCols = ('Type', 'Value')
		displayCols = ('Type', 'Value')
		self.tree = ttk.Treeview(treeFrame, selectmode="browse", columns=dataCols, displaycolumns=displayCols)
		
		
		ysb = ttk.Scrollbar(treeFrame, orient=VERTICAL, command= self.tree.yview)
		self.tree['yscroll'] = ysb.set
		
		# setup column headings
		self.tree.heading('#0', text='Name', anchor=W)
		self.tree.heading('Type', text='Type', anchor=W)
		self.tree.heading('Value', text='Value', anchor=W)
		
		self.tree.column('#0', stretch=0, width=100)
		self.tree.column('Type', stretch=0, width=100)
		self.tree.column('Value', stretch=1, width=120)
		
		# add tree and scrollbars to frame
		self.tree.grid(row=0, column=0, sticky='NSEW')
		ysb.grid(row=0, column=1, sticky='NSE')
		
		self.tree.bind("<Double-1>", self.handle_double_click)
		self.tree.bind('<<TreeviewSelect>>', self.update_options)
		self.tree.bind('<Button-1>', self.handle_click)
		
		
		self.rightFrame = Frame(border)
		self.rightFrame.grid(row=1, column=1, sticky=(N, E), padx=(10,0))
		
		self.rightFrame.columnconfigure(0, weight=0)
		for i in range(0, 3):
			self.rightFrame.rowconfigure(i, weight=0, uniform="MiddleRight")
		
		dimensions = [70, 35]
		
		self._addFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._addFrame.grid(row=0, column=0, sticky=())
		self._addFrame.grid_propagate(0)
		self._addFrame.columnconfigure(0, weight=1)
		self._addFrame.rowconfigure(0, weight=1)
		self._add = Button(self._addFrame, text="Add", command=self.add)
		self._add.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._deleteFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._deleteFrame.grid(row=1, column=0, sticky=(), pady=3)
		self._deleteFrame.grid_propagate(0)
		self._deleteFrame.columnconfigure(0, weight=1)
		self._deleteFrame.rowconfigure(0, weight=1)
		self._delete = Button(self._deleteFrame, text="Delete", command=self.delete_selected)
		self._delete.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._editFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._editFrame.grid(row=2, column=0, sticky=())
		self._editFrame.grid_propagate(0)
		self._editFrame.columnconfigure(0, weight=1)
		self._editFrame.rowconfigure(0, weight=1)
		self._edit = Button(self._editFrame, text="Edit", command=self.edit)
		self._edit.grid(row=0, column=0, sticky=(N, S, E, W))
		
		
		
		#Bottom
		
		
		optionsFrame =  Frame(content)
		optionsFrame.grid(row=1, column=0,padx = 10, pady = 10, sticky=(S, E))
		
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
		
		
		self.populate_tree()
			
		ToplevelObserver.add_element(self)
			
			
			
	def handle_click(self, event):
		""" Disable clicking on the separator to resize the tree """
		
		if self.tree.identify_region(event.x, event.y) == "separator":
			return "break"
			
			
	def handle_double_click(self, event):
		""" Open a variable when double clicked """
		
		if self.tree.identify_region(event.x, event.y) == "separator":
			return "break"
		elif self.tree.identify_region(event.x, event.y) == "cell":
			item = self.tree.identify('item', event.x, event.y)
			self.open(item)	
		
		
	def open(self, iid):
		""" Open a variable for editing """
		
		name = self.tree.item(iid)['text']
		variable = VariableList.tVars[name].copy()
		OpenVariable(variable, self, iid)
		
		
	def add_tree_item(self, index, data):
		""" Add an item to the tree at the index with the speciied data """
		
		iid = self.tree.insert("", index, text=data['name'], values=[data['type'], data['description']])
		return iid
		
		
	def add(self):
		""" Add a new item at the end of the variable list """
		
		name = self.nameEntry.get()
		if len(name) > 0 :
			if VariableList.contains(name):
				if messagebox.askokcancel("Overwrite", "Overwrite Variable " + name + "?", 
				parent=ToplevelObserver.top()):
					self.delete(name)
				else:
					return
					
			variable = VariableList.create_variable(self.variableType.get(), name)
			VariableList.add_element(variable)
			index = len(self.tree.get_children())
			
			data = variable.get_data()
			
			iid = self.add_tree_item(index, data)
			self.treeItems[name] = iid
			self.tree.selection_set(iid)
			self.update_options()
	
	
	def edit(self):
		""" Open and edit selected """
		
		selected = self.tree.selection()
		if(len(selected) == 1):
			self.open(selected[0])
			
	
	def delete_selected(self):
		""" Delete the selected variable from tree """
		
		iid = self.tree.selection()[0]
		prev = self.tree.prev(iid)
		if(prev == ''):
			prev = self.tree.next(iid)
			
		self.tree.selection_set(prev)
		self.delete(self.tree.item(iid)['text'])
		self.update_options()
		
		
	def delete(self, name):
		""" Delete variable from the tree by name """
		
		iid = self.treeItems[name]
		del self.treeItems[name]
		VariableList.remove_element(name)
		self.tree.delete(iid)
		self.update_options()
		
		
	def save_variable(self, variable, iid):
		""" Save the data of the variable at the iid """
		
		name = variable.name
		if VariableList.contains(name):
			self.delete(name)
		if self.tree.exists(iid):
			self.delete(self.tree.item(iid)['text'])
			
		iid = self.add_tree_item(0, variable.get_data())
		self.treeItems[name] = iid
		VariableList.add_element(variable)
		self.tree.selection_set(iid)
		
		
	def populate_tree(self):
		""" Fill the tree with the list of variables """
		
		if self.tree is not None and self.tree.winfo_exists():
			for child in self.tree.get_children(''):
				self.tree.delete(child)
			j = 0 
			self.treeItems = {}
			for key, val in VariableList.tVars.items():
				iid = self.add_tree_item(j, VariableList.tVars[key].get_data())
				self.treeItems[key] = iid
				j=j+1
			self.update_options()
		
		
	def update_options(self, *args):
		""" Update the state of the buttons when the selection changes """
		
		if not self.running and self._add.winfo_exists():
			selected = self.tree.selection()
			if(len(selected) == 1):
				item =  self.tree.selection()[0]
			else:
				item = None
				
			self.acceptButton['state'] = 'normal'
			if item is not None:
				self._edit['state'] = 'normal'
				self._delete['state'] = 'normal'
			else:
				self._edit['state'] = 'disabled'
				self._delete['state'] = 'disabled'
				
				
	def enable_all(self):
		""" Re=enable the buttons when the app is stopped """
		
		self.running = False
		self.update_options()
			
		
	def disable_all(self):
		""" Disable all buttons when the app is playing """
		
		self.running = True
		if self._add is not None and self._add.winfo_exists():
			self._add['state'] = 'disabled'
			self._delete['state'] = 'disabled'
			self._edit['state'] = 'disabled'
			self.acceptButton['state'] = 'disabled'
			
				
	def accept(self, *args):
		""" Save all changes to the variable list and quitt """
		
		VariableList.commit()
		if(self.action is not None):
			self.action.refresh_options()
		self.quit()
		
		
	def quit(self, *args):
		ToplevelObserver.remove_element(self)
		VariableList.editor = None
		self.destroy()
		
		
	
class OpenVariable(Toplevel):
	""" Open and display a variable to edit """
	
	def __init__(self, variable, editor, iid):
		Toplevel.__init__(self)
		self.protocol("WM_DELETE_WINDOW", self.quit)
		self.attributes('-topmost', 'true')
		self.grab_set()
		self.variable = variable
		self.editor = editor
		self.iid = iid
		
		self.winfo_toplevel().minsize(200, 100)
		self.resizable(False, False)
		self.wm_title("Variable")
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		content = Frame(self)
		content.grid(row=0, column=0, padx = 10, pady = 10, sticky=(N, S, E, W))
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		
		#Action
		
		
		self.varFrame = self.variable.display(content)
		
		self.varFrame.columnconfigure(0, weight=1)
		self.varFrame.rowconfigure(0, weight=1)
		
		self.varFrame.grid(row=0, column=0, pady=(0,5), sticky=(N, S, E, W))
		
		
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
		
	
	def enable_all(self):
		""" Re-enable accepting variable changes when program is stopped """
		
		self.acceptButton['state'] = 'normal'
			
		
	def disable_all(self):
		""" Disable accepting variable changes when the program is playing """
		
		self.acceptButton['state'] = 'disabled'
	
	
	def accept(self, *args):
		""" Accept changes and save the variable """
		
		self.variable.save()
		self.editor.save_variable(self.variable, self.iid)
		self.quit()
			
		
	def quit(self, *args):
		ToplevelObserver.remove_element(self)
		self.destroy()

		
class VariableList(object):
	""" Static class stores the list of variables used by the app """
	
	tVars = {}
	vars = {}
	editor = None
	
	def set(name, value):
		VariableList.tVars[name].set(value)
		if(VariableList.editor is not None):
			VariableList.editor.populate_tree()
			
	def get(name):
		return VariableList.tVars[name] 
			
	
	def add_element(x):
		VariableList.tVars[x.name] = x

	
	def remove_element(name):
		VariableList.tVars.pop(name, None)

			
	def contains(name):
		return (name in VariableList.tVars)
		
		
	def replace(vars):
		VariableList.tVars = {}
		VariableList.tVars.update(vars)
		
		
	def create_variable(variableType, name):
		""" Create a new point variable """
	
		variable = None
		if(variableType == "Point"):
			variable = PointVariable(name)
		return variable
		
		
	def reset():
		""" Revert all changes that were made """
		
		copy = {}
		for key, value in VariableList.vars.items():
			copy[key] = value.copy()
		VariableList.tVars = copy
		if(VariableList.editor is not None):
			VariableList.editor.populate_tree()
		
		
	def commit():
		""" Save all changes made to the variables """
		
		copy = {}
		for key, value in VariableList.tVars.items():
			copy[key] = value.copy()
		VariableList.vars = copy
		
		
	def get_data():
		""" Return the variable info to save """
		
		data = []
		for i in VariableList.vars:
			data.append(VariableList.vars[i].get_data())
			
		return data
		
		
	def load_data(data):
		""" Take the dataand create a variable list """
		
		vars = {}
		for varData in data:
			varType = varData['type']
			name = varData['name']
			variable = VariableList.create_variable(varType, name)
			variable.load(varData)
			vars[variable.name] = variable
			
		VariableList.replace(vars)
		VariableList.commit()