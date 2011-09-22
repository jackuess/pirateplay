import cStringIO, urllib2, re, sys
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

class redirect_handler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
		return cStringIO.StringIO(str(headers))

def generate_getcmd(url, **args):
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
						yield next_url
				except ValueError:
					next_url = next_url.replace('/mp4:', '/ -y mp4:') #Add playpath when needed, in a hackish manner
					yield next_url
			else:
				if content == url:
					break

if __name__ == "__main__":
	for cmd in remove_duplicates(generate_getcmd(sys.argv[1], output_file="-")):
		print(cmd)