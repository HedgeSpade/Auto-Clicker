import keyboard
import time
import threading

UPDATE_RATE = 5

class Keybinds():
	def __init__(self, app):
		super(Keybinds, self).__init__()
		self.startVal = ''
		self.pauseVal = ''
		self.app = app
		self.thread = threading.Thread(target=self.run, args=())
		self.thread.start()
		
		
	def stop(self):
		print('k')
		
		
	def run(self):
		while True:
			self.app.test()
			time.sleep(1)
	
	def set_pause(self, key):
		self.pauseVal = key
		if(self.pauseVal == self.startVal):
			self.app.clear_start()
		keyboard.add_hotkey(self.pauseVal, self.app.pause)
		
		
	def clear_pause(self):
		self.pauseVal = ''
		keyboard.remove_hotkey(self.pause)
		
		
	def set_start(self, key):
		self.startVal = key
		if(self.startVal == self.pauseVal):
			self.app.clear_pause()
		keyboard.add_hotkey(self.startVal, self.app.start)
		
		
	def clear_start(self):
		self.startVal = ''
		keyboard.remove_hotkey(self.start)
				
