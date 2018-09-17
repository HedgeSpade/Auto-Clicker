import win32api, win32con
import time
import re
import math
import os
import json
import pyautogui
import VirtualKeystroke
from abc import ABCMeta, abstractmethod
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from ctypes import windll, Structure, c_long, c_int, byref
from abc import ABCMeta, abstractmethod


""" Point structure with (x, y) """
class POINT(Structure):
	_fields_ = [("x", c_int), ("y", c_int)]
	
	
	
class MouseTools():
	""" Tools for getting the position of the mouse or things at the mouse position """
	
	def queryMousePosition():
		""" Return the posion of the mouse """
		
		pt = POINT()
		windll.user32.GetCursorPos(byref(pt))
		return pt
		
		
	def queryPixelColor(pixel):
		""" Get the RGB Hex color of the pixel """
		
		h = windll.user32.GetDC(0)
		color = windll.gdi32.GetPixel(h, pixel.x, pixel.y)
		tup = (MouseTools.red(color), MouseTools.green(color), MouseTools.blue(color))
		return '#%02x%02x%02x' % tup
		
		
	def red(c):
		return c & 0xff
		
	def green(c):
		return (c >> 8) & 0xff
		
	def blue(c):
		return (c >> 16) & 0xff
	
		
def rClicker(e):
    ''' right click context menu for all Tk Entry and Text widgets '''

    try:
        def rClick_Copy(e, apnd=0):
            e.widget.event_generate('<Control-c>')

        def rClick_Cut(e):
            e.widget.event_generate('<Control-x>')

        def rClick_Paste(e):
            e.widget.event_generate('<Control-v>')

        e.widget.focus()

        nclst=[
               (' Cut', lambda e=e: rClick_Cut(e)),
               (' Copy', lambda e=e: rClick_Copy(e)),
               (' Paste', lambda e=e: rClick_Paste(e)),
               ]

        rmenu = Menu(None, tearoff=0, takefocus=0)

        for (txt, cmd) in nclst:
            rmenu.add_command(label=txt, command=cmd)

        rmenu.tk_popup(e.x_root+40, e.y_root+10,entry="0")

    except TclError:
        print (' - rClick menu, something wrong')
        pass

    return "break"


class MouseOptionFrame(Frame):
	''' Custom frame with entry widget and button that can determine the mouse position 
	on click and store it in the entry '''
	 
	def __init__(self, master, pos):
		Frame.__init__(self, master)
		self.master = master
	
		self.columnconfigure(0, weight=1)
		self.columnconfigure(1, weight=1)
		self.rowconfigure(0, weight=1)
		
		self.point = PointEntry(self)
		self.point.insert(pos.x, pos.y)
		pick = Button(self, text="+", width=2, command=self.pick_mouse_position)
		
		self.point.grid(row=0, column=0)
		pick.grid(row=0, column=1)
		
	
	def pick_mouse_position(self):
		""" Create a frame that stores the mouse position when clicked in the Entry widget """
		
		self.t = Toplevel(self.master)
		self.t.resizable(False, False)
		self.t.attributes("-fullscreen", True)
		self.t.attributes('-alpha', 0.2)
		self.t.columnconfigure(0, weight=1)
		self.t.rowconfigure(0, weight=1)
		self.clickframe = Frame(self.t, cursor="cross")
		self.clickframe.grid(column=0, row=0, sticky=(N,S,E,W))
		self.clickframe.bind("<Button-1>", self.set_mouse_position)
		
	def set_mouse_position(self, event):
		""" Store the mouse position in the Entry """
		
		self.t.destroy()
		pt = MouseTools.queryMousePosition()
		self.point.insert(pt.x, pt.y)
		
	def set(self, pt):
		self.point.insert(pt[0], pt[1])
	
	def get(self): 
		return self.point.get()
			
			
class MouseScanFrame(Frame):
	""" A frame with 3 entry widgets that represents an area to scan in """
	
	def __init__(self, master):
		Frame.__init__(self, master)
		
		self.pt = POINT(0,0);
		self.width = 0
		self.height = 0
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		
		scanArea = Frame(self)
		scanArea.grid(row=0, column=0, sticky=(N, W))
		
		
		scanArea.columnconfigure(0, weight=1)
		scanArea.columnconfigure(1, weight=1)
		scanArea.columnconfigure(2, weight=1)
		scanArea.rowconfigure(0, weight=1)
		scanArea.rowconfigure(1, weight=1)
		scanArea.rowconfigure(2, weight=1)
	
		
		lbl2 = Label(scanArea, text='Start:')
		lbl2.grid(row=0, column=0, padx=(0, 5), sticky=(W))
		
		self.ptEntry = PointEntry(scanArea)
		self.ptEntry.grid(row=0, column=1, sticky=(E))
		
		
		
		lbl3 = Label(scanArea, text='Width:')
		lbl3.grid(row=1, column=0, padx=(0, 5), sticky=(W))
		
		self.widthEntry = NumberEntry(scanArea, 6, 6, '0')
		self.widthEntry.grid(row=1, column=1, sticky=(E))

		
		
		lbl3 = Label(scanArea, text='Height:')
		lbl3.grid(row=2, column=0, padx=(0, 5), sticky=(W))
		
		self.heightEntry = NumberEntry(scanArea, 6, 6, '0')
		self.heightEntry.grid(row=2, column=1, sticky=(E))
		
		
		pick = Button(scanArea, text="+", width=2,  command=self.pick_scan_box)
		pick.grid(row=2, column=2, sticky=(E), padx=(5, 0))
	
	
	def pick_scan_box(self):
		""" Click and drag on an area of the screen to scan and store the data in the 3 entry widgets """

		self.t = Toplevel()
		self.t.resizable(False, False)
		self.t.attributes("-fullscreen", True)
		self.t.attributes('-alpha', 0.2)
		self.t.grab_set()
		self.t.columnconfigure(0, weight=1)
		self.t.rowconfigure(0, weight=1)
		self.clickCanvas = Canvas(self.t, cursor="cross")
		self.clickCanvas.grid(column=0, row=0, sticky=(N,S,E,W))
		
		self.mouse_pressed = False
		self.clickCanvas.bind("<ButtonPress-1>", self.OnMouseDown)
		self.clickCanvas.bind("<ButtonRelease-1>", self.OnMouseUp)
		
		
	def OnMouseDown(self, event):
		""" Start the click and drag """
	
		self.pt = MouseTools.queryMousePosition()
		
		self.startStr = '(' + str(self.pt.x) + ', ' + str(self.pt.y) + ')'
		
		self.startText = self.clickCanvas.create_text(self.pt.x, self.pt.y - 10, text=self.startStr)
		self.endText = self.clickCanvas.create_text(self.pt.x, self.pt.y - 10, text=self.startStr)
		
		self.line = self.draw_square_box(self.pt, self.pt)
		self.mouse_pressed = True
		self.poll()
		
	def OnMouseUp(self, event):
		""" Release and store the data """
	
		pt = MouseTools.queryMousePosition()
		start = POINT(pt.x, pt.y)
		if pt.x > self.pt.x:
			start.x = self.pt.x
		if pt.y > self.pt.y:
			start.y = self.pt.y
		
		self.width = int(math.fabs(self.pt.x - pt.x))
		self.widthEntry.insert(str(self.width))
		self.height = int(math.fabs(self.pt.y - pt.y))
		self.heightEntry.insert(str(self.height))
		
		self.ptEntry.insert(str(start.x), str(start.y))
		self.pt = start
		
		self.master.after_cancel(self.after_id)
		self.t.destroy()
	
	
	def poll(self):
		""" Poll to see if the mouse is currently clicked and being dragged """
		
		if self.mouse_pressed:
			self.hold()
			self.after_id = self.master.after(50, self.poll)
			
	
	def hold(self):
		""" While the mouse is held, display the area that is currently being selected """
		
		pt = MouseTools.queryMousePosition()
		self.clickCanvas.delete(self.line)
		self.line = self.draw_square_box(self.pt, pt)
		
		self.clickCanvas.delete(self.startText)
		self.clickCanvas.delete(self.endText)
		endStr = '(' + str(pt.x) + ', ' + str(pt.y) + ')'
		
		if self.pt.y >= pt.y:
			self.startText = self.clickCanvas.create_text(self.pt.x, self.pt.y + 10, text=self.startStr)
			self.endText = self.clickCanvas.create_text(pt.x, pt.y - 10, text=endStr)
		else:
			self.startText = self.clickCanvas.create_text(self.pt.x, self.pt.y - 10, text=self.startStr)
			self.endText = self.clickCanvas.create_text(pt.x, pt.y + 10, text=endStr)
		
		
	def draw_square_box(self, start, end):
		return self.clickCanvas.create_line(start.x, start.y, end.x, start.y, end.x, end.y, start.x, end.y, start.x, start.y, fill='black')
		
		
	def get(self):
		return [self.pt.x, self.pt.y, self.width, self.height]
		
	def set(self, region):
		self.pt = POINT(region[0], region[1])
		self.width = region[2]
		self.height = region[3]
		
		self.ptEntry.insert(self.pt.x, self.pt.y)
		self.widthEntry.insert(self.width)
		self.heightEntry.insert(self.height)
	
		
class NumberEntry(Frame):
	""" Custom entry that only allows numbers """

	def __init__(self, master, char_limit, entry_size, start_text):
		Frame.__init__(self, master)
		self.master = master
		self.startText = start_text
		self.vcmd = (self.register(self.validate),
					'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
					
		text = StringVar()
		text.trace("w", lambda name, index, mode, text = text: self.character_limit(text, char_limit))
		self.c_entry = Entry(self, width=entry_size, validate = 'key', validatecommand = self.vcmd, textvariable = text)
		self.c_entry.config(foreground = 'grey')
		self.c_entry.insert(END, start_text)
		self.c_entry.bind('<FocusIn>', self.on_focusin)
		self.c_entry.bind('<FocusOut>', self.on_focusout)
			
		self.c_entry.bind('<Button-3>',rClicker, add='')
		self.c_entry.grid(column=0, row=0)
		
		
	def insert(self, value):
		self.c_entry.delete(0, "end")
		self.c_entry.insert(END, value)
		
	
	def get(self):
		s = self.c_entry.get()
		if(len(s) < 1 ):
			return 0
		return int(s)
		
		
	def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
		if text.isdigit():
			try:
				if len(value_if_allowed) < 1:
					return True;
				float(value_if_allowed)
				return True
			except ValueError:
				return False
		else:
			return False
			
	
	def character_limit(self, entry_text, length):
		if len(entry_text.get()) > 0:
			entry_text.set(entry_text.get()[:length])
			
	def on_focusin(self, event):
		"""function that gets called whenever entry is clicked"""
		event.widget.delete(0, "end") # delete all the text in the entry
		event.widget.insert(0, '') #Insert blank for user input
		event.widget.config(foreground = 'black')
	   
	def on_focusout(self, event):
		if event.widget.get() == '':
			event.widget.insert(0, self.startText)
			event.widget.config(foreground = 'grey')
			
			

class KeyEntry(Frame):
	""" Custom entry that only allows keystrokes """
	
	def __init__(self, master, entry_size):
		Frame.__init__(self, master)
		self.master = master
		self.keyVal = ''
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		
		self.key = Entry(self, width=entry_size, validate = 'key')
		self.key.grid(row=0, column=0, sticky="ew")
		
		self.key.insert(END, 'None')
		
		self.key.bind('<FocusOut>', self.on_focusout)
		self.key.bind('<Button-1>', self.on_focusin)
		self.key.bind('<Key>', self.set_key)
		self.key['state'] = 'disabled'
	
		
	def set_key(self, event):
		self.key.delete(0, "end")
		s = event.keysym
		if(s == event.char):
			s = s.lower()
		self.key.insert(END, s)
		self.key['state'] = 'disabled'
		
		
	def insert(self, value):
		self.key['state']= 'normal'
		self.key.delete(0, "end")
		self.key.insert(END, value)
		self.key['state']= 'disabled'
		self.keyVal = value
		
		
	def on_focusout(self, event):
		self.key['state']= 'disabled'
		if(len(self.key.get()) < 1):
			self.clear()
		
		
	def on_focusin(self, event):
		self.key['state']= 'normal'
		self.key.delete(0, "end")
		
		
	def get(self):
		temp = self.key.get()
		if(temp == 'None'):
			self.keyVal = ''
		else:
			self.keyVal = temp
		return self.keyVal
		
		
	def clear(self):
		self.key['state']= 'normal'
		self.key.delete(0, "end")
		self.key.insert(END, 'None')
		self.key['state']= 'disabled'
		

class TextEntry(Frame):
	""" Custom text entry (max 180 chars) that only allows printable characters """
	
	def __init__(self, master, char_limit, width, height, start_text):
		Frame.__init__(self, master)
		self.master = master
		self.char_limit = char_limit
		self.startText = start_text
		
		self.columnconfigure(0, weight=0)
		self.columnconfigure(1, weight=0)
		self.rowconfigure(0, weight=1)
					
		text = StringVar()
		text.trace("w", lambda name, index, mode, text = text: self.character_limit(text, char_limit))
		self.c_entry = Text(self, width=width, height=height)
		S = Scrollbar(self)
		
		self.c_entry.grid(row=0, column=0)
		S.grid(row=0, column=1, sticky="ns")
		
		S.config(command=self.c_entry.yview)
		self.c_entry.config(yscrollcommand=S.set)
		self.c_entry.config(foreground = 'grey')
		self.c_entry.insert(END, start_text)
		self.c_entry.bind('<FocusIn>', self.on_click)
		self.c_entry.bind('<FocusOut>', self.on_focusout)
		self.c_entry.bind('<Button-3>',rClicker, add='')
		
		
	def insert(self, value):
		self.c_entry.delete('1.0',END)
		self.c_entry.insert(END, value)
		
	
	def get(self):
		text = self.c_entry.get("1.0", "end-1c")
		if text == self.startText:
			return ''
		else:
			return text
		
	def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
		if(text.isprintable()):
			return True
		else:
			return False
	
	def character_limit(self, entry_text, length):
		text = entry_text.get("1.0", "end-1c")
		if len(text) > 0 and not text == self.startText:
			entry_text.set(text[:length])

			
	def on_click(self, event):
		"""function that gets called whenever entry is clicked"""
		if event.widget.get("1.0", "end-1c") == self.startText:
			event.widget.delete('1.0',END) # delete all the text in the entry
			event.widget.insert('1.0', '') #Insert blank for user input
			event.widget.config(foreground = 'black')
	   
	def on_focusout(self, event):
		text = event.widget.get("1.0", "end-1c")
		if len(text) == 0:
			event.widget.insert('1.0', self.startText)
			event.widget.config(foreground = 'grey')
			
			
class PointEntry(Frame):
	""" Custom entry formatted like (x, y) where x and y values are editable with numbers """
	
	def __init__(self, master):
		Frame.__init__(self, master)
		self.master = master
		self.char_limit = 12
		self.vcmd = (self.register(self.validate),
					'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
					
		text = StringVar()
		self.c_entry = Entry(self, width=12, validate = 'key', validatecommand = self.vcmd, textvariable = text)
		self.c_entry.insert(END, '(0, 0)')
			
		self.c_entry.bind('<Button-3>',rClicker, add='')
		self.c_entry.grid(column=0, row=0)
		
		
	def insert(self, x, y):
		s = self.c_entry.get()
		out = s.split(', ')
		out[0] = out[0].replace('(', '')
		out[1] = out[1].replace(')', '')
		
		self.c_entry.delete(1, 1 + len(out[0]))
		self.c_entry.delete(3, 3 + len(out[1]))
		
		self.c_entry.insert(1, x)
		self.c_entry.insert(3 + len(str(x)), y)
		
	
	def get(self):
		s = self.c_entry.get()
		out = s.split(', ')
		out[0] = out[0].replace("(", "")
		out[1] = out[1].replace(")", "")
		x = 0
		y = 0
		if len(out[0]) > 0:
			x = int(out[0])
		if len(out[1]) > 0:
			y = int(out[1])
		return POINT(x,y)
		
		
	def validate(self, action, index, value_if_allowed, prior_value, text, validation_type, trigger_type, widget_name):
		if bool(re.match('\([0-9]{0,4}, [0-9]{0,4}\)', value_if_allowed)) and len(value_if_allowed) <= self.char_limit:
			return True
		return False
			
	
class ToggledFrame(Frame):
	""" Custom frame that can be toggled on or off with a button """
	
	def __init__(self, parent, text="", *args, **options):
		Frame.__init__(self, parent, *args, **options)

		self.show = IntVar()
		self.show.set(0)
		
		self.columnconfigure(0, weight=1)
		self.rowconfigure(0, weight=1)
		self.rowconfigure(1, weight=1)

		self.title_frame = Frame(self)
		self.title_frame.grid(row=0, column=0, sticky=(W))
		
		self.title_frame.columnconfigure(0, weight=1)
		self.title_frame.columnconfigure(1, weight=1)
		self.title_frame.rowconfigure(0, weight=1)
		self.title_frame.rowconfigure(1, weight=1)

		Label(self.title_frame, text=text).grid(row=0, column=0, padx=(0,10))

		self.toggle_button = ttk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle,
											variable=self.show, style='Toolbutton')
		
		self.toggle_button.grid(row=0, column=1)

		self.sub_frame = Frame(self)

	def toggle(self):
		if bool(self.show.get()):
			self.sub_frame.grid(row=1, column=0, padx=10, pady=10)
			self.toggle_button.configure(text='-')
		else:
			self.sub_frame.grid_forget()
			self.toggle_button.configure(text='+')
			

class ScreenShot(Toplevel):
	""" Specify an area on the dektop, take a screenshot of the area, display the image, and save it """

	def __init__(self, action):
		Toplevel.__init__(self)
		self.protocol("WM_DELETE_WINDOW", self.quit)
		self.attributes('-topmost', 'true')
		self.grab_set()
		self.winfo_toplevel().minsize(200, 100)
		self.resizable(False, False)
		self.wm_title("Screenshot")
		
		self.region = [0, 0, 0, 0]
		self.action = action
		
		content = Frame(self)
		content.grid(row=0, column=0, padx = 10, pady = 10, sticky=(N, S, E, W))
		
		content.columnconfigure(0, weight=1)
		content.rowconfigure(0, weight=1)
		content.rowconfigure(1, weight=1)
		content.rowconfigure(2, weight=1)
		
		self.screenshotFrame = MouseScanFrame(content)
		self.screenshotFrame.grid(row=0, column=0)
		
		imgFrame = Frame(content)
		imgFrame.grid(row=1, column=0, pady=10)
		
		imgFrame.columnconfigure(0, weight=1)
		imgFrame.rowconfigure(0, weight=1)
		
		imageBorder = Frame(imgFrame, width=250, height=250, relief=SUNKEN, borderwidth=2)
		imageBorder.columnconfigure(0, weight=1)
		imageBorder.rowconfigure(0, weight=1)
		imageBorder.grid(row=0, column=0, sticky=(N,W))
		imageBorder.grid_propagate(0)
		
		self.imageLabel = Label(imageBorder)
		self.imageLabel.grid(row=0, column=0, sticky=(N,S,E,W))
		
		bf = Frame(content)
		bf.grid(row=2, column=0, sticky=(E))
		
		bf.columnconfigure(0, weight=1)
		bf.columnconfigure(1, weight=1)
		bf.columnconfigure(2, weight=1)
		bf.rowconfigure(0, weight=1)
		
		Button(bf, text="Capture", command=self.capture).grid(row=0, column=0, sticky=(W), padx = (0,5))
		Button(bf, text="Save", command=self.save_img).grid(row=0, column=1, sticky=(W), padx = (0,5))
		Button(bf, text="Exit", command=self.quit).grid(row=0, column=2, sticky=(W))
		
		ToplevelObserver.hide_all()
	
		
	def capture(self):
		""" Capture and display the image """
		
		self.region = self.screenshotFrame.get()
		self.update_screenshot()
		
	
	def update_screenshot(self):
		""" Display the captured image """
		
		self.region = self.screenshotFrame.get()
		self.im = pyautogui.screenshot(region=self.region)
		
		width = self.region[2]
		height = self.region[3]
		
		maxSize = 240
		
		if width > 0 and height > 0:
			if width > height:
				p = float(maxSize)/float(width)
				width = maxSize
				height = int(float(height) * p)
			else:
				p = float(maxSize)/float(height)
				height = maxSize
				width = int(float(width) * p)
			
			
			resized = self.im.resize((width, height), Image.ANTIALIAS)
			
			temp = ImageTk.PhotoImage(resized)
			
			self.imageLabel.configure(image=temp)
			self.imageLabel.image = temp
		
			

	def save_img(self):
		""" Save the screenshot """
		
		path = "Images"
		file = filedialog.asksaveasfilename(parent=self, initialdir = path, title = "Save As", defaultextension=".png", filetypes = (("png files","*.png"),("all files","*.*")))
		if file:
			self.im.save(file)
			self.action.display_img(file)
			
			
	def quit(self, *args):
		ToplevelObserver.show_all()
		self.destroy()

		
class ToplevelObserver(object):
	""" Static class, holds the list of currently active TopLevel windows """
	
	elements = []
	enable = True

	@staticmethod
	def add_element(x):
		ToplevelObserver.elements.append(x)
		if(ToplevelObserver.enable):
			x.enable_all()
		else:
			x.disable_all()
	
	def remove_element(x):
		ToplevelObserver.elements.remove(x)
		
	def top():
		return ToplevelObserver.elements[-1]
		
	def hide_all():
		""" Hides all active windows """
		
		for i in ToplevelObserver.elements:
			i.iconify()
		
	def show_all():
		""" shows all active windows """
	
		for i in ToplevelObserver.elements:
			i.update()
			i.deiconify()

	def enable_all():
		""" Enable all butoons when app is stopped """
		
		ToplevelObserver.enable = True
		for i in ToplevelObserver.elements:
			i.enable_all()
			
	def disable_all():
		""" Disable all butoons when app is playing """
		
		ToplevelObserver.enable = False
		for i in ToplevelObserver.elements:
			i.disable_all()
