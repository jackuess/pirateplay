import sys, urllib2, xml.sax

class DCHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.capture = False
		self.data = ''
		self.count = 1
	def startElement(self, name, attrs):
		if name == 'Subtitle':
			self.data += '%s\n%s,%s --> %s,%s\n' % (attrs.get('SpotNumber'), attrs.get('TimeIn')[:8], attrs.get('TimeIn')[9:12], attrs.get('TimeOut')[:8], attrs.get('TimeOut')[9:12])
		elif name == 'p':
			self.data += '%s\n%s,%s --> %s,%s\n' % (self.count, attrs.get('begin')[:8], attrs.get('begin')[9:], attrs.get('end')[:8], attrs.get('end')[9:])
			self.capture = True
			self.count += 1
		elif name == 'br':
			self.data += '\n'
		elif name == 'Text':
			self.capture = True
	def endElement(self, name):
		if name == 'Subtitle':
			self.data += '\n'
		elif name == 'Text':
			self.capture = False
			self.data += '\n'
		elif name == 'p':
			self.capture = False
			self.data += '\n\n'
	def characters(self, ch):
		if self.capture: self.data += ch

def xml2srt(url):
	handler = DCHandler()
	xml.sax.parseString(urllib2.urlopen(url).read(), handler)
	return unicode(handler.data)

if __name__ == "__main__":
	print xml2srt(sys.argv[1])