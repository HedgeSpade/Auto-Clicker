import win32api, win32con
import time
import threading
import json
import keyboard
import os
import configparser
from ctypes import windll, Structure, c_long, byref
from abc import ABCMeta, abstractmethod
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from Tree import Tree
from Tools import MouseTools
from Tools import KeyEntry
from Tools import NumberEntry
from Tools import ToplevelObserver
from Variables import VariableList
		
		
def resource_path(relative_path):
	""" Get absolute path to resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)
		
		
class Application(Tk):
	""" Application """

	def __init__(self):
		""" Initialize the Frame """
		
		super(Application, self).__init__()
		self.title("Auto Clicker")
		self.geometry('{}x{}'.format(600, 520))
		self.protocol("WM_DELETE_WINDOW", self.quit)
		
		# local variables
		
		self.saveLoctaion = None
		self.filename = None
		self.playing = False
		self.stopped = True
		self.playKey = ''
		self.stopKey = ''
		self.minimize = IntVar(value=1)
		self.timestr = StringVar()
		self.instructions = {}
		self._start = 0.0
		self._running = 0
		self.pauseTime = 0
		self.step = 0
		self.cycle = 0
		
		# layout menu widgets
		
		self.menubar = Menu(self)
		self.configure(menu=self.menubar)

		menu = Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label="File", menu=menu)
		menu.add_command(label="New", command=self.new)
		menu.add_command(label="Open...", command=self.open)
		menu.add_command(label="Save", command=self.quick_save)
		menu.add_command(label="Save As...", command=self.save_as)
		
		
		# create the main containers
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		self.contentContainer = Frame(self, padx=0, pady=0)
		
		self.contentContainer.columnconfigure(0, weight=1)
		self.contentContainer.rowconfigure(0, weight=1)
		
		self.content = Frame(self.contentContainer, padx=10, pady=10)
		
		self.contentContainer.grid(column=0, row=0, sticky=(N, S, E, W))
		self.content.grid(column=0, row=0, sticky=(N, S, E, W))
		
		self.content.columnconfigure(0, weight=1)
		self.content.rowconfigure(0, weight=0)
		self.content.rowconfigure(1, weight=1)
		self.content.rowconfigure(2, weight=0)
		
		self.create_widgets()
		self.winfo_toplevel().minsize(600, 520)
		self.set_time(0)
		self.load_settings()
		self.update()
		
		
	
	def create_widgets(self):
		""" Create widgets for the main containers """
		
		# Top Frame
		
		top = Frame(self.content)
		top.grid(row=0, column=0, sticky=(N, E, W))
		
		top.columnconfigure(0, weight=0)
		top.columnconfigure(1, weight=0)
		top.columnconfigure(2, weight=1)
		top.rowconfigure(0, weight=0)
		

		playpath = resource_path("play.png")
		self.play_img = PhotoImage(file=playpath)
		self.play_img = self.play_img.subsample(10)
		
		pausepath = resource_path("pause.png")
		self.pause_img = PhotoImage(file=pausepath)
		self.pause_img = self.pause_img.subsample(10)
		
		stoppath = resource_path("stop.png")
		self.stop_img = PhotoImage(file=stoppath)
		self.stop_img = self.stop_img.subsample(10)
		
		
		buttonFrame = Frame(top)
		buttonFrame.columnconfigure(0, weight=1)
		buttonFrame.columnconfigure(1, weight=1)
		buttonFrame.rowconfigure(0, weight=1)
		buttonFrame.grid(row=0, column=0, sticky=(W))
		
		self.playButton = Button(buttonFrame, image=self.play_img, width="20", height="20", command=self.play)
		self.playButton.image=self.play_img
		self.playButton.grid(row=0, column=0, padx=(0,5), sticky=(W))
		
		self.stopButton = Button(buttonFrame, image=self.stop_img, width="20", height="20", command=self.stop)
		self.stopButton.image=self.stop_img
		self.stopButton.grid(row=0, column=1, sticky=(W))
		
		
		stateFrame = Frame(top, width=50, heigh=20)
		stateFrame.place(relx=.50, rely=0.40, anchor=CENTER)
		stateFrame.grid_propagate(0)
		
		stateFrame.columnconfigure(0, weight=1)
		stateFrame.columnconfigure(1, weight=1)
		stateFrame.rowconfigure(0, weight=1)
		
		self.stateFrame1 = Frame(stateFrame, width=20, heigh=20, relief="ridge", borderwidth=2)
		self.stateFrame1.grid(row=0, column=0, padx=(0,10), sticky=(W))
		self.stateFrame1.grid_propagate(0)
		
		self.stateFrame2 = Frame(stateFrame, width=20, heigh=20, relief="ridge", borderwidth=2)
		self.stateFrame2.grid(row=0, column=1, sticky=(W))
		self.stateFrame2.grid_propagate(0)
		
		
		self.stateFrame1.config(bg="#eeefff")
		self.stateFrame2.config(bg="#eeefff")
		
		
		runtimeFrame = Frame(top)
		runtimeFrame.columnconfigure(0, weight=1)
		runtimeFrame.columnconfigure(1, weight=1)
		runtimeFrame.rowconfigure(0, weight=1)
		runtimeFrame.grid(row=0, column=2, sticky=(E))
		
		runtimelbl = Label(runtimeFrame, text="Runtime:")
		runtimelbl.grid(row=0, column=0, padx=(0,5), sticky=(W))
		
		self.runtimeval = Label(runtimeFrame, text="0:00")
		self.runtimeval.grid(row=0, column=1, sticky=(W))
		
		
		# Middle Frame/Tree
		
		self.tree = Tree()
		treeFrame = self.tree.display(self.content)
		treeFrame.grid(row=1, column=0, pady=(10,0), sticky=(N, S, E, W))
		
		
		# Bottom Frame
		
		self._bottomFrame = Frame(self.content)
		self._bottomFrame.grid(row=2, column=0, sticky=(N, S, E, W))
		
		self._bottomFrame.columnconfigure(0, weight=1)
		self._bottomFrame.columnconfigure(1, weight=1)
		self._bottomFrame.rowconfigure(0, weight=0)
		
		
		# Bottom Left Frame
		
		bottomLeft = Frame(self._bottomFrame)
		bottomLeft.grid(row=0, column=0, sticky=(N,S,W))
		bottomLeft.columnconfigure(0, weight=1)
		bottomLeft.rowconfigure(0, weight=0)
		
		
		bottomLeftBorder = Frame(bottomLeft, relief=GROOVE, borderwidth=2)
		bottomLeftBorder.grid(row=0, column=0, pady= (20, 0), sticky=(N, W))
		
		bottomLeftBorder.columnconfigure(0, weight=1)
		bottomLeftBorder.rowconfigure(0, weight=1)
		
		bottomLeftFrame = Frame(bottomLeftBorder)
		bottomLeftFrame.grid(row=0, column=0, padx=10, pady=10, sticky=(N, W))
		
		bottomLeftFrame.columnconfigure(0, weight=1)
		bottomLeftFrame.columnconfigure(1, weight=1)
		bottomLeftFrame.columnconfigure(2, weight=1)
		bottomLeftFrame.columnconfigure(3, weight=1)
		bottomLeftFrame.rowconfigure(0, weight=0)
		bottomLeftFrame.rowconfigure(1, weight=0)
		
		
		Label(bottomLeft, text='Keybinds').place(relx=.08, rely=0.20,anchor=W)

		
		Label(bottomLeftFrame, text="Play/Pause:", width=8, anchor= "w").grid(row=0, column=0, sticky="w", padx=(0,10))
		self.playKeyEntry = KeyEntry(bottomLeftFrame, 10)
		self.playKeyEntry.grid(row=0, column=1, sticky="ew", padx=(0,5))
		self.playKeySet = Button(bottomLeftFrame, text="Set", width=8, command=self.set_play_keybind)
		self.playKeySet.grid(row=0, column=2, sticky=(E), padx=(0,5))
		self.playKeyClear = Button(bottomLeftFrame, text="Clear", width=8, command=self.clear_play_keybind)
		self.playKeyClear.grid(row=0, column=3, sticky=(E))
		
		Label(bottomLeftFrame, text="Stop:", width=8, anchor=(W)).grid(row=1, column=0, sticky=(W), padx=(0,10))
		self.stopKeyEntry = KeyEntry(bottomLeftFrame, 10)
		self.stopKeyEntry.grid(row=1, column=1, sticky=(E,W), padx=(0,5))
		self.stopKeySet = Button(bottomLeftFrame, text="Set", width=8, command=self.set_stop_keybind)
		self.stopKeySet.grid(row=1, column=2, sticky=(E), padx=(0,5))
		self.stopKeyClear = Button(bottomLeftFrame, text="Clear", width=8, command=self.clear_stop_keybind)
		self.stopKeyClear.grid(row=1, column=3, sticky=(E))
		
		
		# Bottom Right Frame
		
		self._bottomRightFrame = Frame(self._bottomFrame)
		self._bottomRightFrame.grid(row=0, column=1, pady= (10, 0), sticky=(N, S, E))
		
		self._bottomRightFrame.columnconfigure(0, weight=1)
		self._bottomRightFrame.columnconfigure(1, weight=1)
		self._bottomRightFrame.rowconfigure(0, weight=1)
		self._bottomRightFrame.rowconfigure(1, weight=0)
		self._bottomRightFrame.rowconfigure(2, weight=0)
		

		check = Checkbutton(self._bottomRightFrame, text="Mininmize on start", variable=self.minimize)
		check.grid(row=0, column=0, columnspan=2, pady=(0,5), sticky=(S,E))
		
		self._lblCycles = Label(self._bottomRightFrame, text="Program Cycles:")
		self._lblMouse = Label(self._bottomRightFrame, text='Mouse Position:')
		
		self._cyclesVal = NumberEntry(self._bottomRightFrame, 9, 9, '1')
		
		pos = MouseTools.queryMousePosition()
		self._mouse = Label(self._bottomRightFrame, text=pos, width=8)

		
		self._lblCycles.grid(row=1, column=0, padx=(0, 10), pady=(0,5), sticky=(S, W))
		self._lblMouse.grid(row=2, column=0, padx=(0, 10), sticky=(S, W))
		self._cyclesVal.grid(row=1, column=1, pady=(0,5), sticky=(S, E))
		self._mouse.grid(row=2, column=1, sticky=(S, E))
		
		ToplevelObserver.add_element(self)
		
		
	def load_settings(self):
		""" Load program settings: keybinds and minimize on play option """
		
		configpath = 'AutoClicker.ini'
		self.settings = configparser.ConfigParser()
		self.settings._interpolation = configparser.ExtendedInterpolation()
		self.settings.read(configpath)
		playKey = self.settings.get('Keybinds', 'play')
		stopKey = self.settings.get('Keybinds', 'stop')
		self.saveLocation = self.settings.get('Save Path', 'path')
		
		if int(self.settings.get('Minimize on play', 'minimize')):
			self.minimize.set(1)
		else:
			self.minimize.set(0)
		
		if not playKey == "None":
			self.playKeyEntry.insert(playKey)
			self.set_play_keybind()
			
		if not stopKey == "None":
			self.stopKeyEntry.insert(stopKey)
			self.set_stop_keybind()
	
	
	def save_settings(self):
		""" Save program settings: keybinds and minimize on play option """
		
		configpath = 'AutoClicker.ini'
		cfgfile = open(configpath,'w')
		self.settings.set('Keybinds','play', self.playKeyEntry.get())
		self.settings.set('Keybinds','stop', self.stopKeyEntry.get())
		self.settings.set('Minimize on play', 'minimize', str(self.minimize.get()))
		self.settings.set('Save Path', 'path', self.saveLocation)
		
	
		self.settings.write(cfgfile)
		cfgfile.close()
		
		
	def update(self):
		""" Update runtime counter time and Mouse Position widgets """
		
		pos = MouseTools.queryMousePosition()
		result = "( " + str(pos.x) + ", " + str(pos.y) + " )"
		self._mouse['text'] = result
		
		if(self.playing):
			elapsedtime = time.time() - self._start
			self.set_time(elapsedtime)	
		
		self.after(50, self.update)
		
		
	def set_time(self, elap):
		""" Set time value for the runtime widget """
		
		minutes = int(elap/60)
		seconds = int(elap - minutes*60.0)
		hseconds = int((elap - minutes*60.0 - seconds)*100)                
		self.timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))
		self.runtimeval.configure(text=self.timestr.get())
		
		
	def new(self):
		""" Clear the actions tree and reset """
		
		self.tree.reset()
		self.filename = None
		self.title("Auto Clicker")
		
	
	def open(self):
		""" Open a .json file of saved data and load the data from the file """
		
		path = self.saveLocation
		if(not os.path.isdir(path)):
			path = os.path.abspath(".")
			
		filename = filedialog.askopenfilename(parent=self, initialdir = path, title = "Select file", filetypes = (("json files","*.json"),("all files","*.*")))
		
		try:
			with open(filename,'r') as f:
				data = f.read()
				d = json.loads(data)
				self.tree.load_data(d['actions'])
				VariableList.load_data(d['variables'])
				self._cyclesVal.insert(d['cycles'])
					
				self.filename = filename
				self.title(os.path.basename(self.filename))
		except:
			print("No file exists")
	
	
	def save_as(self):
		""" Save program data in a .json file """
			
		path = self.saveLocation
		if(not os.path.isdir(path)):
			path = os.path.abspath(".")
			
		filename = filedialog.asksaveasfilename(parent=self, initialdir = path, title = "Save As", 
		defaultextension=".json", filetypes = (("json files","*.json"),("all files","*.*")))
		try:
			with open(filename,'w') as f:
				d = {}
				d['actions'] = self.tree.get_data()
				d['variables'] = VariableList.get_data()
				d['cycles'] = self._cyclesVal.get()
				data = json.dumps(d)
				f.write(data)
				f.close()
				
				self.filename = filename
				self.saveLocation = os.path.dirname(self.filename)
				self.title(os.path.basename(self.filename))
		except:
			print("Save Failed")
		
		
	def quick_save(self):
		""" Quick save data as a .json file """
	
		try:
			with open(self.filename, 'w') as f:
				d = {}
				d['actions'] = self.tree.get_data()
				d['variables'] = VariableList.get_data()
				d['cycles'] = self._cyclesVal.get()
				data = json.dumps(d)
				f.write(data)
				f.close()
		except:
			self.save_as()
		
		
	def set_stop_keybind(self):
		""" Set the stop keybind """
		
		val = self.stopKeyEntry.get()
		if(len(val) > 0):
			self.stopKey = val
			keyboard.add_hotkey(self.stopKey, self.stop)
			if(self.stopKey == self.playKey):
				self.clear_play_keybind()
		
		
	def clear_stop_keybind(self):
		""" Clear the stop keybind """
		
		if(len(self.stopKey) > 0):
			self.stopKeyEntry.clear()
			self.stopKey = ''
			keyboard.remove_hotkey(self.stop)
		
		
	def set_play_keybind(self):
		""" Set the Play/Pause keybind """
		
		val = self.playKeyEntry.get()
		if(len(val) > 0):
			self.playKey = val
			keyboard.add_hotkey(self.playKey, self.play)
			if(self.playKey == self.stopKey):
				self.clear_stop_keybind()
			
		
	def clear_play_keybind(self):
		""" Clear the Play/Pause keybind """
		
		if(len(self.playKey) > 0):
			self.playKeyEntry.clear()
			self.playKey = ''
			keyboard.remove_hotkey(self.play)
		
		
	def disable_all(self):
		""" Disable all buttons while playing """
		
		self.tree.disable_all()
		self.playKeySet['state'] = 'disabled'
		self.playKeyClear['state'] = 'disabled'
		self.stopKeySet['state'] = 'disabled'
		self.stopKeyClear['state'] = 'disabled'
		self.menubar.entryconfig("File", state="disabled")
		
			
	def enable_all(self):
		""" Ensable all buttons while stopped """
		
		self.tree.enable_all()
		self.playKeySet['state'] = 'normal'
		self.playKeyClear['state'] = 'normal'
		self.stopKeySet['state'] = 'normal'
		self.stopKeyClear['state'] = 'normal'
		self.menubar.entryconfig("File", state="normal")
		self.playButton.config(image=self.play_img)
		self.playButton.image=self.play_img
		
			
	
	def run(self):
		""" Play the next action in the instruction list """
		
		# Reached the end of the instruction list
		if(self.step > (len(self.instructions) - 1)):
			if(self.cycles > 0):
				self.cycles = self.cycles - 1
				self.reset(0)
			else:
				self.stop()
				return
			
		action = self.instructions[self.step]
		
		# Delay, then do the action
		for i in range(int(action.repeat) + 1):
			self.tree.select(self.step)
			win32api.Sleep(int(action.delay))
			if self.playing:
				if not action.play():
					self.play()
			else:
				return
			
		# Move to the next instruction
		self.step = self.step + 1
		if self.playing:
			self.run()
			
			
	def play(self):
		""" Play/Pause the application """
		
		# If already playing, pause the app
		if(self.playing):
			# Pause
			self.playing = False
			self.playButton.config(image=self.play_img)
			self.playButton.image=self.play_img
			self.stateFrame1.config(bg="#eeefff")
			self.stateFrame2.config(bg="#ffdf7f")
			self.pauseTime = time.time()
			elapsedtime = time.time() - self._start    
			self.set_time(elapsedtime)
			if self.minimize.get():
				ToplevelObserver.show_all()
		else:
			# Play
			# If starting, commit the changes
			if(self.stopped):
				# Start
				if not self.tree.is_playable():
					return
				self.cycles = self._cyclesVal.get()
				if(self.cycles == 0):
					self.stop()
					return
				self.cycles = self.cycles - 1
				self._start = time.time()
				self.reset(self.tree.get_start())
				VariableList.commit()
				
			if self.minimize.get():
					ToplevelObserver.hide_all()
				
			self.playButton.config(image=self.pause_img)
			self.playButton.image=self.pause_img
			
			self.stateFrame1.config(bg="#32bf07")
			self.stateFrame2.config(bg="#eeefff")
		
			if self.pauseTime > 0:
				self._start = self._start + (time.time() - self.pauseTime)
			self.playing = True
			ToplevelObserver.disable_all()
			self.stopped = False
			
			self.thread = threading.Thread(target=self.run, args=(), daemon=True)
			self.thread.start()

			
	def stop(self):
		""" Stop the application """
		
		self.stopped = True
		self._elapsedtime = 0.0    
		self.pauseTime = 0
		self.set_time(self._elapsedtime)
		self.playing = False
		self.stateFrame1.config(bg="#eeefff")
		self.stateFrame2.config(bg="#eeefff")
		ToplevelObserver.enable_all()
		if self.minimize.get():
			ToplevelObserver.show_all()

		
	def reset(self, step):
		""" Reset the application """
		
		self.instructions = self.tree.actionList
		self.step = step
		self.tree.select(self.step)
		
		
	def quit(self):
		""" Save the current settings and exit the app """
		
		self.save_settings()
		sys.exit()
	
		
if __name__ == "__main__":
	app = Application()
	app.mainloop()
	
	
	

	

