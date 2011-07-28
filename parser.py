# coding=utf8

import json, pickle, sys, urllib2, xml.sax

import tidylib
from PyQt4 import QtCore, QtXmlPatterns, QtNetwork

class EpisodeListHandler(xml.sax.ContentHandler):
	def __init__(self):
		self.episode_list = {}
		pass
	def startElement(self, name, attrs):
		if name == 'episode':
			self.curr_data = ""
			self.curr_episode = {'title' : attrs.get('title'), 'href' : attrs.get('href')}
	def endElement(self, name):
		if name == 'episode':
			self.episode_list.update({self.curr_episode['title'] : self.curr_episode['href']})
			print "\t* Added episode: \033[32m" + self.curr_episode['title'] + '\033[0m'
	def characters(self, ch):
		pass#self.curr_data += ch

class ProgramListHandler(xml.sax.ContentHandler):
	def __init__(self, episode_query, episode_tidy_opts, episode_encoding):
		self.programlist = {}
		self.episode_query = episode_query
		self.episode_tidy_opts = episode_tidy_opts
		self.episode_encoding = episode_encoding
		pass
	def startElement(self, name, attrs):
		self.curr_data = ""
		if name == 'program':
			self.curr_program = {'title' : attrs.get('title'), 'href' : attrs.get('href')}
	def endElement(self, name):
		if name == 'program':
			print "Processing " + '\033[31m' + self.curr_program['title'] + '\033[0m'
			
			try:
				xml_data = http_xquery(self.curr_program['href'], self.episode_query, self.episode_tidy_opts, self.episode_encoding)
			
				self.listhandler = EpisodeListHandler()
				self.sax_parser = xml.sax.make_parser()
				self.sax_parser.setContentHandler(self.listhandler)
				xml.sax.parseString(xml_data.encode('utf8'), self.listhandler)
				#self.curr_program.update({'list' : self.listhandler.episode_list })
				
				self.programlist.update({self.curr_program['title'] : self.listhandler.episode_list})
			except (urllib2.HTTPError, urllib2.URLError):
				print "HTTP Error: Couldn't fetch " + self.curr_program['title']
			
	def characters(self, ch):
		pass#self.curr_data += ch

def http_xquery(url, query, tidy_opts = None, encoding = 'utf8'):
	document = urllib2.urlopen(url).read()
	
	if not tidy_opts == None:
		document, tidy_errors = tidylib.tidy_document(document, tidy_opts)
	
	qt_query = QtXmlPatterns.QXmlQuery()
	qt_query.setFocus(str(document))
	qt_query.setQuery(query)
	xml_data = unicode(qt_query.evaluateToString(), encoding)
	
	return xml_data

rss_query = """
		let $items := /rss/channel/item
		return
		<program>
		{ for $item in $items
		return <episode title="{$item/title}" href="{$item/link}">{$item/description}</episode> }
		</program>
		"""
programming = {
			'SVT'	:
					{
						'url'		:	'http://svtplay.se/alfabetisk',
						'program_tidy_opts':	{ 'input_xml' : 1, 'char_encoding' : 'utf8' },
						'program_query'	:	"""
									declare default element namespace "http://www.w3.org/1999/xhtml";
									let $shows := (//ul[@class="leter-list"]/li/a)
									return
									<programlist name="SVT" encoding="utf-8">
										{ for $show in $shows
										return <program href="http://feeds.svtplay.se/v1/video/list/{replace($show/string(@href), '/t/', '')}?expression=full" title="{$show/text()}"><![CDATA[fitta]]></program> }
									</programlist>
									(:return (<p>{//ul[@class="leter-list"]/li/a/string(@href))[2]}</p>):)
									""",
						'episode_tidy_opts':	None,
						'episode_query'	:	"""
									let $items := /rss/channel/item
									return
									<program>
										{ for $item in $items
											return <episode title="{$item/title}" href="{$item/link}">{$item/description}</episode> }
									</program>
									""",
						'episode_encoding':	'utf-8' },
			'TV3'	:
					{
						'url'		:	'http://www.tv3play.se/program',
						'program_tidy_opts':	{ 'output_xhtml' : 1, 'char_encoding' : 'utf8' },
						'program_query'	:	"""
									declare default element namespace "http://www.w3.org/1999/xhtml";
									let $shows := (//div[@id="main-content"]//a[@href])
									return
									<programlist name="SVT" encoding="utf-8">
									{ for $show in $shows
									return <program href="http://tv3play.se{$show/string(@href)}" title="{$show/text()}"></program> }
									</programlist>
									""",
						'episode_tidy_opts':	{ 'output_xhtml' : 1, 'char_encoding' : 'utf8' },
						'episode_query'	:	"""
									declare default element namespace "http://www.w3.org/1999/xhtml";
									let $episodes := //table[@class="clearfix clip-list video-tree"]//tbody/tr/th
									return
									<programlist name="TV3" encoding="utf-8">
									{ for $episode in $episodes
										return
										<episode href="http://tv3play.se{$episode/a/attribute::href}" title="{($episode/parent::*/preceding-sibling::*//strong)[last()]/text()}, Avsnitt {$episode/following-sibling::td[@class="col2"]/text()}"></episode> }
									</programlist>
									""",
						'episode_encoding':	'utf-8' },
			'TV4'	:
					{
						'url'		:	'http://www.tv4play.se/a_till_o_lista',
						'program_tidy_opts':	{ 'output_xml' : 1, 'new_blocklevel_tags' : 'section,footer,nav,header', 'char_encoding' : 'utf8' },
						'program_query'	:	"""
									let $shows := //ul/li/h3/a
									return
									<programlist name="TV4" encoding="utf-8">
										{ for $show in $shows
											return <program href="http://www.tv4play.se/rss/{$show/string(@href)}" title="{$show/text()}"></program> }
									</programlist>
									""",
						'episode_tidy_opts':	None,
						'episode_query'	:	rss_query,
						'episode_encoding':	'latin-1'} }

app = QtCore.QCoreApplication(sys.argv)
qt_query = QtXmlPatterns.QXmlQuery()

tidylib.BASE_OPTIONS = {}

def parse_programming(service):
	xml_data = http_xquery(service['url'], service['program_query'], service['program_tidy_opts'])
	print xml_data

	listhandler = ProgramListHandler(service['episode_query'], service['episode_tidy_opts'], service['episode_encoding'])
	sax_parser = xml.sax.make_parser()
	sax_parser.setContentHandler(listhandler)
	xml.sax.parseString(xml_data.encode('utf8'), listhandler)
	
	return listhandler.programlist

data = {}
data.update({'SVT' : parse_programming(programming['SVT'])})
data.update({'TV3' : parse_programming(programming['TV3'])})
#data.append({'title' : 'TV4', 'list' : parse_programming(programming['TV4'])})
output = open('data.pkl', 'wb')
pickle.dump(data, output)
output.close()
output = open('data.json', 'wb')
json.dump(data, output)
output.close()