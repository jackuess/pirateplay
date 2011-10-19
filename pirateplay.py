#!/usr/bin/python2

import cStringIO, getopt, urllib2, re, sys
from services import service
from kanal5 import get_kanal5

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

def convert_rtmpdump(rtmpdump_cmd):
	meta, cmd = rtmpdump_cmd.split('\n')
	args = cmd[9:].split() # Strip 'rtmpdump ' and split
	optlist = getopt.getopt(args, 'r:o:W:y:', ['rtmp=', 'swfVfy=', 'playpath='])[0]
	rtmp_string = ""
	for optpair in optlist:
		if optpair[0] == '--rtmp' or optpair[0] == '-r':
			rtmp_string = "%s%s" % (optpair[1], rtmp_string)
		elif optpair[0] == '--swfVfy' or optpair[0] == '-W':
			rtmp_string += ' swfVfy=1 swfUrl=' + optpair[1]
		elif optpair[0] == '--playpath' or optpair[0] == '-y':
			rtmp_string += ' playpath=' + optpair[1]
	return meta + '\n' + rtmp_string

class redirect_handler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return cStringIO.StringIO(str(headers))

def generate_getcmd(url, rtmpdump_cmds = True, **args):
	urllib2.install_opener(urllib2.build_opener(redirect_handler()))
	for channel_service in service:
		match_vars = args
		content = url
		for item in channel_service:
			for match in re.finditer(item['re'], content, re.DOTALL):
				match_vars.update(del_nones(match.groupdict()))
				next_url = item['template'] % match_vars
				req = urllib2.Request(next_url)
				if item.has_key('user-agent-string'):
					req.add_header('User-Agent', item['user-agent-string'])
				try:
					content = urllib2.urlopen(req).read()
				except urllib2.URLError: #Kanal5
					if next_url[:9] == 'kanal5://':
						content = get_kanal5(next_url[9:]).encode('ascii')
					else:
						if rtmpdump_cmds: yield next_url
						else: yield convert_rtmpdump(next_url)
				except ValueError:
					next_url = next_url.replace('/mp4:', '/ -y mp4:') #Add playpath when needed, in a hackish manner
					if rtmpdump_cmds: yield next_url
					else: yield convert_rtmpdump(next_url)
			else:
				if content == url:
					break

if __name__ == "__main__":
	for cmd in remove_duplicates(generate_getcmd(sys.argv[1], True, output_file="-")):
		print(cmd)
