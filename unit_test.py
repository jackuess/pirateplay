from lxml import etree
from os import system
from traceback import format_exc
from urllib2 import urlopen

from pirateplay import generate_getcmd, remove_duplicates

ansi = {'red': '\033[31m',
	'green': '\033[32m',
	'blue': '\033[36m',
	'reset': '\033[0m'}

feed_urls = ['http://feeds.svtplay.se/v1/video/list/96238?expression=full&mode=plain',
	'http://www.tv3play.se/rss/recent',
	'http://www.tv4play.se/rss/dokumentarer',
	'http://www.kanal5play.se/rss?type=PROGRAM',
	'http://www.tv6play.se/rss/mostviewed',
	'http://www.tv8play.se/rss/recent',
	'http://www.kanal9play.se/rss?type=PROGRAM']

for feed_url in feed_urls:
	f = urlopen(feed_url)
	tree = etree.parse(f)
	url = tree.xpath('/rss/channel/item[1]/link/text()')[0]
	network = tree.xpath('/rss/channel/title/text()')[0]
	title = tree.xpath('/rss/channel/item[1]/title/text()')[0]
	print(''.join((ansi['blue'], network)))
	print(''.join((title, ansi['reset'])))
	try:
		cmds = remove_duplicates(generate_getcmd(url, True, output_file='-'))
		if len(cmds) > 0:
			print('%sFine!%s' % (ansi['green'], ansi['reset']))
			print(''.join(('\t', cmds[0][:130].replace('\n', '\n\t'))))
			#system('ffplay "%s"' % cmds[0].splitlines()[1])
		else:
			print('%sNothing found for %s!%s' % (ansi['red'], title, ansi['reset']))
	except:
		print('%s%s broken!%s' % (ansi['red'], title, ansi['reset']))
		print(''.join(('\t', format_exc().replace('\n', '\n\t'))))