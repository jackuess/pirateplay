#!/usr/bin/python2

import cStringIO, getopt, urllib2, re, sys
from os import system
from services import service, get_brightcove_streams, build_brightcove_dict
from kanal5 import get_kanal5
from httplib import BadStatusLine

def del_nones(dict):
	for item in dict.items():
		if item[1] == None:
			del dict[item[0]]
	return dict

def remove_duplicates(cmds):
	dict = {}
	for cmd in cmds:
		dict[cmd] = 1
	return dict.keys()

def convert_rtmpdump(rtmpdump_cmd, convert):
	meta, cmd = rtmpdump_cmd.split('\n')
	# Do we realy want to convert?
	if convert and cmd.startswith('rtmpdump'):
		args = cmd[9:].split() # Strip 'rtmpdump ' and split
		optlist = getopt.getopt(args, 'r:o:W:y:a:v', ['rtmp=', 'swfVfy=', 'playpath=', 'app=', 'live'])[0]
		rtmp_string = ""
		for option, value in optlist:
			if option == '--rtmp' or option == '-r':
				rtmp_string = "%s%s" % (value.strip('"'), rtmp_string)
			elif option == '--swfVfy' or option == '-W':
				rtmp_string += ' swfVfy=1 swfUrl=' + value.strip('"')
			elif option == '--playpath' or option == '-y':
				rtmp_string += ' playpath=' + value.strip('"')
			elif option == '--app' or option == '-a':
				rtmp_string += ' app=' + value.strip('"')
			elif option == '--live' or option == '-v':
				rtmp_string += ' live=1'
		return meta + '\n' + rtmp_string
	# ..or just pass through?
	else:
		return rtmpdump_cmd

class redirect_handler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return cStringIO.StringIO(str(headers))

def generate_getcmd(url, librtmp = False, **args):
	yielded = False
 	#urllib2.install_opener(urllib2.build_opener(urllib2.HTTPHandler(debuglevel=1)))
	urllib2.install_opener(urllib2.build_opener(redirect_handler()))
	for channel_service in service:
		match_vars = {'sub' : ''}
		match_vars.update(args)
		content = url
		for item in channel_service:
			next_re = item['re'] % match_vars
			for match in re.finditer(next_re, content, re.DOTALL):
				match_vars.update(del_nones(match.groupdict()))
				
				next_url = item['template'] % match_vars
				next_url = item.get('decode', lambda (url): url)(next_url)
				req = urllib2.Request(next_url)
				
				if 'post-template' in item:
					req.add_data(item['post-template'] % match_vars)
				
				for header, value in item.get('headers', {}).items():
					req.add_header(header, value)
				
				try:
					response = urllib2.urlopen(req)
					content = response.read()
					response.close()
				except urllib2.URLError: #Kanal5
					if next_url.startswith('kanal5://'):
						content = get_kanal5(next_url[9:]).encode('ascii')
					elif next_url.startswith('brightcove:'):
						brightcove_params = build_brightcove_dict(next_url[11:])
						content = get_brightcove_streams(**brightcove_params).encode('ascii')
					else:
						yielded = True
						yield convert_rtmpdump(next_url, librtmp)
				except ValueError:
					yielded = True
					yield convert_rtmpdump(next_url, librtmp)
				except BadStatusLine as excp:
					yielded = True
					break
			else:
				if content == url:
					break
		else:
			if yielded: break


class Modes:
	Print, Play, Save = range(3)

if __name__ == "__main__":
	if system('which ffplay > /dev/null') != 0:
		sys.exit('\nffplay not found.\nPirateplay needs ffplay to play your streams.')
	
	opts, values = getopt.getopt(sys.argv[1:], 'pys:', ['print', 'play', 'save='])
	mode = Modes.Play
	for option, value in opts:
			if option == '--print' or option == '-p':
				mode = Modes.Print
			elif option == '--play' or option == '-y':
				mode = Modes.Play
			elif option == '--save' or option == '-s':
				mode = Modes.Save
	i = 0
	exe = []
	for cmd in remove_duplicates(generate_getcmd(sys.argv[len(sys.argv)-1], True, output_file="-")):
		if mode == Modes.Print:
			print cmd
		else:
			exe.append(None)
			desc, exe[i] = cmd.splitlines()
			i += 1
			if desc == '#':
				desc = '#Stream %d' % i
			print('%d. %s' % (i, desc.strip('#')))
	
	if mode == Modes.Play:
		system('ffplay "' + exe[int(raw_input('Choose stream: '))-1] + '"')
