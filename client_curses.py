# coding=utf8

import curses, curses.textpad, pickle, urllib2, shlex, subprocess, sys, thread, traceback

#sys.path.append('/home/chucky/utveckling/pirateplay')
from pirateplay import generate_getcmd, remove_duplicates

class Menu():
	def __init__(self, data, scr, y, x):
		self.set_data(data)
		self.__indexstack = []
		self.__curr_selected = 0
		self.__x = x
		self.__y = y
		self.__y_offset = 0
		self.__window = scr
		self.has_focus = False
	def set_focus(self, gets_focus):
		self.has_focus = gets_focus
		self.draw()
	def update_list(self):
		new_list = self.__data
		try:
			for i in self.__indexstack:
				new_list = new_list[i]['list']
			self.__curr_list = new_list
			return True
		except KeyError:
			return False
	def navigate(self, dy, dx):
		updated = True
	
		self.__curr_selected += dy
		
		if self.__curr_selected < 0:
			self.__curr_selected = 0
		elif self.__curr_selected > len(self.__curr_list)-1:
			self.__curr_selected = len(self.__curr_list)-1
		
		if self.__curr_selected > self.__y_offset+9:
			self.__y_offset += dy
		elif self.__curr_selected < self.__y_offset:
			self.__y_offset = self.__curr_selected
		
		if dx == 1:
			self.__indexstack.append(self.__curr_selected)
			if self.update_list():
				self.__curr_selected = 0
				self.__y_offset = 0
			else:
				self.__indexstack.pop()
				updated = False
		elif dx == -1:
			try:
				self.__curr_selected = self.__indexstack.pop()
				if self.__curr_selected > self.__y_offset+9:
					self.__y_offset = self.__curr_selected
				updated = self.update_list()
			except IndexError:
				updated = False
		
		self.draw()
		return updated
	def draw(self):
		self.__window.clear()
		for i in range(self.__y_offset, len(self.__curr_list[:10])+self.__y_offset):
			if i == self.__curr_selected and self.has_focus: attr = curses.A_STANDOUT
			else: attr = 0
			self.__window.move(self.__y+i-self.__y_offset, self.__x)
			self.__window.addstr(self.__curr_list[i]['title'].encode('utf-8'), attr)
		#self.__window.refresh()
		self.__window.noutrefresh()
	def push_char(self, char):
		if self.has_focus:
			if char == curses.KEY_UP:	return self.navigate(-1, 0)
			elif char == curses.KEY_DOWN:	return self.navigate(1, 0)
			elif char == curses.KEY_RIGHT:	return self.navigate(0, 1)
			elif char == curses.KEY_LEFT:	return self.navigate(0, -1)
		else:
			self.draw()
			return True
	def set_data(self, data):
		self.__data = data
		self.__curr_list = data
	def get_current(self, key):
		return self.__curr_list[self.__curr_selected][key]

def dict2list(dict):
		new_list = []
		try:
			for key, value in sorted(dict.items(), key=lambda item: item[0]):
				next_dict = dict2list(value)
				if next_dict != False:
					new_list.append({'title' : key, 'list' : dict2list(value), 'data' : None})
				else:
					new_list.append({'title' : key, 'data' : value})
			return new_list
		except AttributeError:
			return False

def main():
	def print_help(s):
		help_win.clear()
		help_win.addstr(s)
		help_win.noutrefresh()
		curses.doupdate()
	def download(filename, cmd):
		child = subprocess.Popen(shlex.split(cmd + ' -o ' + filename), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		complete = False
		buffered = ''
		start = False
		while True:
			out = child.stderr.read(7)
			if out == '' and child.poll() != None:
				print_help('Nedladdning klar!')
				break
			elif len(out) > 1:
				if out[0] == '(' and out[1] != 'c':
					print_help('Laddar ner - ' + out[1:out.find(')')])

	selected_item = 0
	
	curses.start_color()
	curses.noecho()
	curses.cbreak()
	curses.curs_set(0)
	
	stdscr.keypad(1)
	#stdscr.nodelay(1)
	logo_name = 'Pirateplayer'
	curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
	logo_attr = curses.color_pair(1)
	stdscr.addstr(1, 2, '  ', logo_attr)
	stdscr.addstr(1, 2+len(logo_name)+6, '  ', logo_attr)
	stdscr.addstr(2, 2, '   ', logo_attr)
	stdscr.addstr(2, 2+len(logo_name)+5, '   ', logo_attr)
	stdscr.addstr(2, 6, logo_name)
	stdscr.addstr(3, 2, '  ', logo_attr)
	stdscr.addstr(3, 2+len(logo_name)+6, '  ', logo_attr)
	stdscr.noutrefresh()
	
	#pkl_file = open('data.pkl', 'rb')
	pkl_file = urllib2.urlopen('http://pirateplay.se/data.pkl')
	data = pickle.load(pkl_file)
	
	data_list = dict2list(data)
	menu = Menu(data_list, curses.newwin(10, stdscr.getmaxyx()[1]-2, 5, 2), 0, 0)
	play_menu = Menu([], curses.newwin(5, 20, 16, 2), 0, 0)
	
	help_win = curses.newwin(5, stdscr.getmaxyx()[1]-2, 25, 2)
	
	print_help('Navigera med piltangenterna\nQ för att avsluta')
	menu.set_focus(True)
	curses.doupdate()
	
	href = ''
	cmd = ''
	
	while True:
		c = stdscr.getch()
		
		if c == ord('q'): break
			
		if not menu.push_char(c):
			data = menu.get_current('data')
			
			if data:
				streams = []
				for rtmp_cmd in remove_duplicates(generate_getcmd(data.encode('utf-8'))):
					streams.append(
								{
									'title' : rtmp_cmd.splitlines()[0],
									'data' 	: None,
									'list' 	: [
											{'title' : 'play', 'data' : rtmp_cmd.splitlines()[1]},
											{'title' : 'download', 'data' : rtmp_cmd.splitlines()[1]}]})
				play_menu.set_data(streams)
				play_menu.set_focus(True)
				menu.set_focus(False)
		elif not play_menu.push_char(c):
			title = play_menu.get_current('title').encode('utf-8')
			data = play_menu.get_current('data')
			
			if title == "play" and data:
				data.encode('utf-8')
				rtmpdump_p = subprocess.Popen(shlex.split(data), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				mplayer_p = subprocess.Popen(['mplayer', '-'], shell=False, stdin=rtmpdump_p.stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			elif title == "download" and data:
				print_help('Ange filnamn - avsluta med Enter:\n>')
				curses.echo()
				file_name = help_win.getstr(1, 2)
				curses.noecho()
				#print_help('Downloading ' + file_name)
				thread.start_new_thread(download, (file_name, data))
			else:
				play_menu.set_data([])
				play_menu.set_focus(False)
				menu.set_focus(True)
			
		
		curses.doupdate()
			
	restore_screen()

def restore_screen():
	curses.nocbreak()
	curses.echo()
	curses.curs_set(1)
	curses.endwin()

stdscr = curses.initscr()

if __name__ == '__main__':
	try:
		main()
	except:
		restore_screen()
		traceback.print_exc()