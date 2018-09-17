from tkinter import *
from tkinter import ttk
from Actions import LeftClick
from Actions import RightClick
from Actions import MoveMouse
from Actions import PressKey
from Actions import HoldKey
from Actions import WriteText
from Actions import DetectImage
from Actions import OpenAction
from Variables import VariableEditor
from Tools import NumberEntry


class Tree():
	""" Treeview that contains the instructions, and buttons to add, delete, and edit the actions """

	def __init__(self):
		self.actionList = []
		self.actionType = StringVar()
		self.allDisabled = False
		self.start = None

	
	def display(self, master):
		""" Create the tree as a Treeview, create the action options above the tree, and create 
			the buttons that interact with the tree """
		
		self.master = master
		self.content = Frame(master)
	
		self.content.columnconfigure(0, weight=1)
		self.content.columnconfigure(1, weight=1)
		self.content.columnconfigure(2, weight=0)
		self.content.rowconfigure(0, weight=0)
		self.content.rowconfigure(1, weight=1)
	
	
		# Action options
		
		
		choices = [ 'Left Click', 'Right Click', 'Mouse Move', 'Press Key', 'Hold Key',
					'Write Text', 'Detect Image']
		self.actionType.set('Left Click')
		
		actionChoiceFrame = Frame(self.content)
		
		actionChoiceFrame.columnconfigure(0, weight=1)
		actionChoiceFrame.columnconfigure(1, weight=1)
		actionChoiceFrame.rowconfigure(0, weight=1)
		
		lblAction = Label(actionChoiceFrame, text='Action:')
		lblAction.grid(row=0, column=0, padx=(0,10), sticky=(W))
		
		# Action type
		actionChoice = Frame(actionChoiceFrame, width=120, height=30)
		actionChoice.grid_propagate(0)
		actionChoice.columnconfigure(0, weight=1)
		actionChoice.rowconfigure(0, weight=1)
		action = OptionMenu(actionChoice, self.actionType, *choices)
		action.grid(row=0, column=0, sticky=(N, S, E, W))
		actionChoice.grid(row=0, column=1, sticky=(E))
		
		actionChoiceFrame.grid(row=0, column=0, sticky=(N, W))
		
		
		#Delay Repeat
		delayRepeatFrame = Frame(self.content)
		delayRepeatFrame.grid(row=0, column=1, sticky=(E))
		
		delayRepeatFrame.columnconfigure(0, weight=1)
		delayRepeatFrame.columnconfigure(1, weight=1)
		delayRepeatFrame.columnconfigure(2, weight=1)
		delayRepeatFrame.rowconfigure(0, weight=1)
		
		delayFrame = Frame(delayRepeatFrame)
		delayFrame.grid(row=0, column=0, sticky=(N, W), pady = 5)
		
		delayFrame.columnconfigure(0, weight=1)
		delayFrame.columnconfigure(1, weight=1)
		delayFrame.rowconfigure(0, weight=1)
		
		lblDelay = Label(delayFrame, text='Delay(ms):')
		self.delayVal = NumberEntry(delayFrame, 9, 9, 0)

		lblDelay.grid(row=0, column=0, sticky=(E))
		self.delayVal.grid(row=0, column=1, sticky=(E))
		
		repeatFrame = Frame(delayRepeatFrame)
		repeatFrame.grid(row=0, column=1, sticky=(N, E), pady = 5)
		
		repeatFrame.columnconfigure(0, weight=1)
		repeatFrame.columnconfigure(1, weight=1)
		repeatFrame.rowconfigure(0, weight=1)
		
		lblRepeat = Label(repeatFrame, text='Repeat:')
		self.repeatVal = NumberEntry(repeatFrame, 9, 9, 0)
		
		lblRepeat.grid(row=0, column=0, sticky=(E), padx = 5)
		self.repeatVal.grid(row=0, column=1, sticky=(E))
		
		self.changeActionSettings = Button(delayRepeatFrame, text="S", command=self.change_action_settings)
		self.changeActionSettings.grid(row=0, column=2, padx=(5,0))
		
		
		#Treeview Frame
		
		
		self.leftFrame = Frame(self.content, relief="ridge", borderwidth=2)
		self.leftFrame.grid(row=1, column=0, columnspan = 2, sticky=(N, S, E, W))
		
		self.leftFrame.columnconfigure(0, weight=1)
		self.leftFrame.rowconfigure(0, weight=1)
		
		
		treeFrame = Frame(self.leftFrame)
		treeFrame.pack(side=TOP, fill=BOTH, expand=Y)
		
		treeFrame.rowconfigure(0, weight=1)
		treeFrame.columnconfigure(0, weight=1)
		treeFrame.columnconfigure(1, weight=0)
		
		
		# create the tree and scrollbars
		dataCols = ('Action', 'Details', 'Delay', 'Repeat')  
		displayCols = ('Action', 'Details', 'Delay', 'Repeat') 
		self.tree = ttk.Treeview(treeFrame, selectmode="browse", columns=dataCols, displaycolumns=displayCols)
		self.tree.bind('<<TreeviewSelect>>', self.update_options)
		
		
		ysb = ttk.Scrollbar(treeFrame, orient=VERTICAL, command= self.tree.yview)
		self.tree['yscroll'] = ysb.set
		
		# setup column headings
		self.tree.heading('#0', text='Step', anchor=W)
		self.tree.heading('Action', text='Action', anchor=W)
		self.tree.heading('Details', text='Details', anchor=W)
		self.tree.heading('Delay', text='Delay', anchor=W)
		self.tree.heading('Repeat', text='Repeat', anchor=W)
		
		
		self.tree.column('#0', stretch=0, width=60)
		self.tree.column('Action', stretch=0, width=100)
		self.tree.column('Details', stretch=1, width=120)
		self.tree.column('Delay', stretch=0, width=60)
		self.tree.column('Repeat', stretch=0, width=60)
		
		# add tree and scrollbars to frame
		self.tree.grid(row=0, column=0, sticky='NSEW')
		ysb.grid(row=0, column=1, sticky='NSE')
		
		self.tree.bind("<Double-1>", self.handle_double_click)
		self.tree.bind('<<TreeviewSelect>>', self.update_options)
		self.tree.bind('<Button-1>', self.handle_click)
		self.tree.bind('<Button-3>', self.handle_right_click)
		
		
		self.tree.tag_configure('breakpoint', background="red", foreground="white")
		self.tree.tag_configure('start', background="green", foreground="white")
		
		
		# Buttons Frame
	
		
		self.rightFrame = Frame(self.content)
		self.rightFrame.grid(row=1, column=2, sticky=(N, E), padx=(10,0))
		
		self.rightFrame.columnconfigure(0, weight=0)
		for i in range(0, 8):
			self.rightFrame.rowconfigure(i, weight=0, uniform="MiddleRight")
		
		dimensions = [70, 35]
		
		self._addFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._addFrame.grid(row=0, column=0, sticky=(), pady=(0, 3))
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
		self._editFrame.grid(row=2, column=0, sticky=(), pady=(0, 3))
		self._editFrame.grid_propagate(0)
		self._editFrame.columnconfigure(0, weight=1)
		self._editFrame.rowconfigure(0, weight=1)
		self._edit = Button(self._editFrame, text="Edit", command=self.edit)
		self._edit.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._upFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._upFrame.grid(row=3, column=0, sticky=(), pady=3)
		self._upFrame.grid_propagate(0)
		self._upFrame.columnconfigure(0, weight=1)
		self._upFrame.rowconfigure(0, weight=1)
		self._up = Button(self._upFrame, text="Up", command=self.up)
		self._up.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._downFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._downFrame.grid(row=4, column=0, sticky=(), pady=3)
		self._downFrame.grid_propagate(0)
		self._downFrame.columnconfigure(0, weight=1)
		self._downFrame.rowconfigure(0, weight=1)
		self._down = Button(self._downFrame, text="Down", command=self.down)
		self._down.grid(row=0, column=0, sticky=(N, S, E, W))

		self._topFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._topFrame.grid(row=5, column=0, sticky=(), pady=3)
		self._topFrame.grid_propagate(0)
		self._topFrame.columnconfigure(0, weight=1)
		self._topFrame.rowconfigure(0, weight=1)
		self._top = Button(self._topFrame, text="Top", command=self.top)
		self._top.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._bottomFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._bottomFrame.grid(row=6, column=0, sticky=(), pady=3)
		self._bottomFrame.grid_propagate(0)
		self._bottomFrame.columnconfigure(0, weight=1)
		self._bottomFrame.rowconfigure(0, weight=1)
		self._bottom = Button(self._bottomFrame, text="Bottom", command=self.bottom)
		self._bottom.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self._variableFrame = Frame(self.rightFrame, width=dimensions[0], height=dimensions[1])
		self._variableFrame.grid(row=7, column=0, sticky=(), pady=3)
		self._variableFrame.grid_propagate(0)
		self._variableFrame.columnconfigure(0, weight=1)
		self._variableFrame.rowconfigure(0, weight=1)
		self._variable = Button(self._variableFrame, text="Variables", command=self.edit_variables)
		self._variable.grid(row=0, column=0, sticky=(N, S, E, W))
		
		self.populate_tree()
		
		return self.content
		
	
	def handle_click(self, event):
		""" Disable clicking on the separator to resize the tree """
		
		if self.tree.identify_region(event.x, event.y) == "separator":
			return "break"
			
			
	def handle_right_click(self, event):
		""" Create right click options for the cells in the tree """
		
		if self.tree.identify_region(event.x, event.y) == "separator":
			return "break"
		elif self.tree.identify_region(event.x, event.y) == "cell":
			item = self.tree.identify('item', event.x, event.y)
			menu = Menu(self.master, tearoff=0)
			if(item == self.start):
				menu.add_command(label="Remove Start", state=NORMAL, command=self.remove_start)
			elif("breakpoint" in self.tree.item(item, "tags")):
				menu.add_command(label="Remove Breakpoint", state=NORMAL, command= lambda:self.remove_breakpoint(item))
			else:
				menu.add_command(label="Set Start", state=NORMAL, command= lambda:self.add_start(item))
				menu.add_command(label="Set Breakpoint", state=NORMAL, command= lambda:self.add_breakpoint(item))
			menu.post(event.x_root, event.y_root)
			
			
	def handle_double_click(self, event):
		""" Open an action when double clicked """
		
		if self.tree.identify_region(event.x, event.y) == "separator":
			return "break"
		elif self.tree.identify_region(event.x, event.y) == "cell":
			item = self.tree.identify('item', event.x, event.y)
			self.open(item)	
	
	
	def add_tree_item(self, index, data):
		""" Add an item to the tree at the index with the speciied data """
		
		iid =  self.tree.insert("", index, text='', values=[data['action'], 
							data['description'], data['delay'], data['repeat']])
		return iid
					
		
	def add(self):
		""" Add a new item directly to the end of the instruction list """
		
		index = self.tree.index(self.tree.selection()) + 1
		action = self.create_action(self.actionType.get())
		
		delay = self.delayVal.get()
		action.delay = delay
		repeat = self.repeatVal.get()
		action.repeat = repeat
		
		self.actionList.insert(index, action)
		self.tree.selection_set(self.add_tree_item(index, action.get_data()))
		self.update_descriptions()
		
		
	def delete_selected(self):
		""" Delete the selected item from the tree """
	
		iid = self.tree.selection()[0]
		prev = self.tree.prev(iid)
		if(prev == ''):
			prev = self.tree.next(iid)
		
		index = self.tree.index(iid)
		del self.actionList[index]
		if iid == self.start:
			self.start = None
		self.tree.delete(iid)
		self.tree.selection_set(prev)
		
		self.update_descriptions()
		
		
	def open(self, iid):
		""" Open the action in the tree with the iid """
	
		action = self.actionList[self.tree.index(iid)].copy()
		OpenAction(action, self, iid)
		
		
	def select(self, index):
		""" Select tree item at the index """
		
		if(index < len(self.tree.get_children(''))):
			self.tree.selection_set(self.tree.get_children('')[index])
		
		
	def get_selection(self):
		""" Returns the selected action """
		
		selected = self.tree.selection()
		return self.tree.index(selected[0])
			
			
	def edit(self):
		""" Open the selected action for editing """
		
		selected = self.tree.selection()
		if(len(selected) == 1):
			self.open(selected[0])
		
		
	def save_action(self, action, iid):
		""" Save the data of the action at iid """
	
		index = self.tree.index(iid)
		self.actionList[index] = action 
		self.tree.delete(iid)
		iid = self.add_tree_item(index, action.get_data())
		self.tree.selection_set(iid)
		self.update_descriptions()
		self.update_options()
		return iid
		
		
	def change_action_settings(self):
		""" Set the delay, repeat, and action type of the action """
	
		iid = self.tree.selection()[0]
		
		action = self.actionList[self.tree.index(iid)]
		if(not self.actionType.get() == action.actionType):
			action = self.create_action(self.actionType.get())
	
		action.delay = self.delayVal.get()
		action.repeat = self.repeatVal.get()
		
		self.save_action(action, iid)
	
	
	def move_action(self, index, index1):
		""" Move an action in the tree from index to index1 """
		
		action = self.actionList[index]
		del self.actionList[index]
		self.actionList.insert(index1, action)
	
	
	def up(self):
		""" Move selected action up one slot """
	
		iid = self.tree.selection()[0]
		index = self.tree.index(iid)
		if(index > 0):
			self.tree.move(iid, '', index - 1)
			self.move_action(index, index - 1)
		self.update_descriptions()
			
			
	def down(self):
		""" Move selected action down one slot """
	
		iid = self.tree.selection()[0]
		index = self.tree.index(iid)
		items = len(self.tree.get_children(''))
		if(index < items):
			self.tree.move(iid, '', index + 1)
			self.move_action(index, index + 1)
		self.update_descriptions()
			
			
	def top(self):
		""" Move selected action to the top of the tree """
		
		iid = self.tree.selection()[0]
		index = self.tree.index(iid)
		self.tree.move(iid, '', 0)
		self.move_action(index, 0)
		self.update_descriptions()
			
			
	def bottom(self):
		""" Move selected action to the bottom of the tree """
	
		iid = self.tree.selection()[0]
		index = self.tree.index(iid)
		items = len(self.tree.get_children(''))
		self.tree.move(iid, '', items)
		self.move_action(index, items)
		self.update_descriptions()
		
		
	def edit_variables(self):
		""" Open variable editor """
		
		VariableEditor()
		
		
	def update_descriptions(self):
		""" Update the descriptions of every action """
		
		i = 1
		children = self.tree.get_children('')
		for child in children:
			self.tree.item(child, text=str(i))
			i += 1
		
		
	def populate_tree(self):
		""" Fill the tree with the list of actions """
		
		self.start = None
		for child in self.tree.get_children(''):
			self.tree.delete(child)
		for i in range(0, len(self.actionList)):
			self.tree.selection_set(self.add_tree_item(i, self.actionList[i].get_data()))
			
		self.update_descriptions()
		self.update_options()
		
		
	def get_data(self):
		""" Return the data of all actions in the tree """
		
		data = []
		for i in range(0, len(self.actionList)):
			data.append(self.actionList[i].get_data())
			
		return data
		
	
	def load_data(self, data):
		""" Load the data into the tree """
		
		self.reset()
		for actionData in data:
			actionType = actionData['action']
			action = self.create_action(actionType)
			action.load(actionData)
			self.actionList.append(action)
		
		self.populate_tree()
		
		
	def create_action(self, actionType):
		""" Create and return a new action of type actionType """
		
		action = None
		if(actionType == "Left Click"):
			action = LeftClick()
		elif(actionType == "Right Click"):
			action = RightClick()
		elif(actionType == "Mouse Move"):
			action = MoveMouse()
		elif(actionType == "Press Key"):
			action = PressKey()
		elif(actionType == "Hold Key"):
			action = HoldKey()
		elif(actionType == "Write Text"):
			action = WriteText()
		elif(actionType == "Detect Image"):
			action = DetectImage()
		return action
			

	def update_options(self, *args):
		""" Update the state of the buttons when the selection changes """
		
		if(not self.allDisabled):
			selected = self.tree.selection()
		
			if(len(selected) == 1):
				action =  self.tree.selection()[0]
			else:
				action = None
				
			if action is not None:
				values = self.tree.item(action)['values']
				# print(item)
				self.repeatVal.insert(values[3])
				self.delayVal.insert(values[2])
				self.actionType.set(values[0])
				self._edit['state'] = 'normal'
				self._delete['state'] = 'normal'
				self._up['state'] = 'normal'
				self._down['state'] = 'normal'
				self._top['state'] = 'normal'
				self._bottom['state'] = 'normal'
				self.changeActionSettings['state'] = 'normal'
			else:
				self._edit['state'] = 'disabled'
				self._delete['state'] = 'disabled'
				self._up['state'] = 'disabled'
				self._down['state'] = 'disabled'
				self._top['state'] = 'disabled'
				self._bottom['state'] = 'disabled'
				self.changeActionSettings['state'] = 'disabled'
			
			
	def disable_all(self):
		""" Disable all buttons when the app is playing """
	
		self.allDisabled = True
		self._add['state'] = 'disabled'
		self._edit['state'] = 'disabled'
		self._delete['state'] = 'disabled'
		self._up['state'] = 'disabled'
		self._down['state'] = 'disabled'
		self._top['state'] = 'disabled'
		self._bottom['state'] = 'disabled'
		self.changeActionSettings['state'] = 'disabled'
		
		self.tree.unbind("<Double-1>")
		self.tree.unbind('<<TreeviewSelect>>')
		self.tree.unbind('<Button-3>')
		
		
	def enable_all(self):
		""" Re=enable the buttons when the app is stopped """
		
		self.allDisabled = False
		self._add['state'] = 'normal'
		self.update_options()
		
		self.tree.bind("<Double-1>", self.handle_double_click)
		self.tree.bind('<<TreeviewSelect>>', self.update_options)
		self.tree.bind('<Button-3>', self.handle_right_click)
			
			
	def copy(self):
		""" Copy the tree and return the copy """
		
		copy = Tree()
		actions = []
		for action in self.actionList:
			actions.append(action.copy())
		copy.actionList = actions
		return copy
		
		
	def reset(self):
		""" Empty the tree """
		
		self.actionList = []
		self.populate_tree()
		
		
	def is_playable(self):
		""" Check to see if any action is missing data making it unplayable """
		
		i = 1
		for action in self.actionList:
			if not action.is_playable(i):
				return False
			i = i + 1
		return True
		
		
	def add_start(self, iid):
		""" Mark an action as the action to start from """
	
		self.remove_start()
		self.start = iid
		self.tree.item(iid, tags="start")
		
		
	def remove_start(self):
		""" Remove the start, making the start point at 0 """
	
		if self.start is not None:
			self.tree.item(self.start, tags=())
			self.start = None
			
			
	def get_start(self):
		""" Return the start point of the app """
	
		if self.start is not None:
			return self.tree.index(self.start)
		else:
			return 0
		
		
	def add_breakpoint(self, iid):
		""" Mark an action as a breakpoint, the app will pause when it reaches a breakpoint """
	
		self.actionList[self.tree.index(iid)].breakpoint = True
		self.tree.item(iid, tags="breakpoint")
		
		
	def remove_breakpoint(self, iid):
		""" Remove a breakpoint """
	
		self.actionList[self.tree.index(iid)].breakpoint = False
		self.tree.item(iid, tags=())
	