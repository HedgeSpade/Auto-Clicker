import win32api, win32con
import time
		   
VK_CODE = {
	
	'Backspace':0x08,
	'Tab':0x09,
	'Clear':0x0C,
	'Enter':0x0D,
	'Shift_L':0xA0,
	'Shift_R':0xA1,
	'Control_L':0xA2,
	'Control_R':0xA3,
	'Alt_L':0x12,
	'Alt_R':0x12,
    'Pause':0x13,
    'Caps_Lock':0x14,
    'Escape':0x1B,
    'space':0x20,
    'page_up':0x21,
    'page_down':0x22,
    'End':0x23,
    'Home':0x24,
    'Left':0x25,
    'Up':0x26,
    'Right':0x27,
    'Down':0x28,
    'Select':0x29,
    'Print':0x2A,
    'Execute':0x2B,
    'print_screen':0x2C,
    'Insert':0x2D,
    'Delete':0x2E,
    'Help':0x2F,
    '0':0x30,
    '1':0x31,
    '2':0x32,
    '3':0x33,
    '4':0x34,
    '5':0x35,
    '6':0x36,
    '7':0x37,
    '8':0x38,
    '9':0x39,
    'a':0x41,
    'b':0x42,
    'c':0x43,
    'd':0x44,
    'e':0x45,
    'f':0x46,
    'g':0x47,
    'h':0x48,
    'i':0x49,
    'j':0x4A,
    'k':0x4B,
    'l':0x4C,
    'm':0x4D,
    'n':0x4E,
    'o':0x4F,
    'p':0x50,
    'q':0x51,
    'r':0x52,
    's':0x53,
    't':0x54,
    'u':0x55,
    'v':0x56,
    'w':0x57,
    'x':0x58,
    'y':0x59,
    'z':0x5A,
    'F1':0x70,
    'F2':0x71,
    'F3':0x72,
    'F4':0x73,
    'F5':0x74,
    'F6':0x75,
    'F7':0x76,
    'F8':0x77,
    'F9':0x78,
    'F10':0x79,
    'F11':0x7A,
    'F12':0x7B,
    'F13':0x7C,
    'F14':0x7D,
    'F15':0x7E,
    'F16':0x7F,
    'F17':0x80,
    'F18':0x81,
    'F19':0x82,
    'F20':0x83,
    'F21':0x84,
    'F22':0x85,
    'F23':0x86,
    'F24':0x87,
    'Num_Lock':0x90,
    'Scroll_Lock':0x91,
    '+':0xBB,
    ',':0xBC,
    '-':0xBD,
    '.':0xBE,
    '/':0xBF,
    '`':0xC0,
    ';':0xBA,
    '[':0xDB,
    '\\':0xDC,
    ']':0xDD,
    "'":0xDE,
    '`':0xC0}
		   
		   
def press(buttons):
    '''
    one press, one release.
    accepts as many arguments as you want. e.g. press('left_arrow', 'a','b').
    '''
    for i in buttons:
        win32api.keybd_event(VK_CODE[i], 0,0,0)
        time.sleep(.01)
        win32api.keybd_event(VK_CODE[i],0 ,win32con.KEYEVENTF_KEYUP ,0)
           
		   
def pressAndHold(t, buttons):
	for i in buttons:
		win32api.keybd_event(VK_CODE[i], 0, 0, 0)
	stop = time.time() + (t/1000)
	while time.time() < stop:
		time.sleep(0.01)
		for i in buttons:
			win32api.keybd_event(VK_CODE[i], 0, 0, 0)
	for i in buttons:
		win32api.keybd_event(VK_CODE[i], 0, win32con.KEYEVENTF_KEYUP, 0)
		time.sleep(0.01)
		

def typer(string=None,*args):
	timeDelay = 0.01
	for i in string:
		if i == ' ':
			win32api.keybd_event(VK_CODE['space'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['space'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '!':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['1'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['1'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '@':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['2'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['2'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '{':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['['], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['['],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '?':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['/'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['/'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == ':':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE[';'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE[';'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '"':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['\''], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['\''],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '}':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE[']'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE[']'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '#':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['3'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['3'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '$':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['4'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['4'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '%':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['5'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['5'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '^':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['6'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['6'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '&':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['7'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['7'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '*':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['8'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['8'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '(':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['9'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['9'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == ')':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['0'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['0'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '_':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['-'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['-'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '=':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['+'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['+'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '~':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['`'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['`'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '<':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE[','], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE[','],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i == '>':
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE['.'], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE['.'],0 ,win32con.KEYEVENTF_KEYUP ,0)

		elif i.isupper():
			i = i.lower()
			win32api.keybd_event(VK_CODE['Shift_L'], 0,0,0)
			win32api.keybd_event(VK_CODE[i], 0,0,0)
			win32api.keybd_event(VK_CODE['Shift_L'],0 ,win32con.KEYEVENTF_KEYUP ,0)
			win32api.keybd_event(VK_CODE[i],0 ,win32con.KEYEVENTF_KEYUP ,0)
			
		elif i == '\n':
			win32api.keybd_event(VK_CODE['Enter'], 0,0,0)
			win32api.keybd_event(VK_CODE['Enter'],0 ,win32con.KEYEVENTF_KEYUP ,0)
    
		elif i == '\t':
				win32api.keybd_event(VK_CODE['Tab'], 0,0,0)
				win32api.keybd_event(VK_CODE['Tab'],0 ,win32con.KEYEVENTF_KEYUP ,0)
	
		else:    
			win32api.keybd_event(VK_CODE[i], 0,0,0)
			# time.sleep(timeDelay)
			win32api.keybd_event(VK_CODE[i],0 ,win32con.KEYEVENTF_KEYUP ,0)
			
		time.sleep(timeDelay)