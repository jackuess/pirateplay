service = [
		[
			{	'service-name':		'SVT-play',
			#	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
			#	'template'	:	'http://svtplay.se/%(url)s'},
				're'		:	r'(http://)?(www\.)?svtplay.se/(?P<path>(t|v)/\d+)',
				'template'	:	'http://svtplay.se/popup/minispelare/%(path)s'},
			#{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)',
			#{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*subtitle=(?P<sub>[^&]+).*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)',
			{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)?(?P<url>rtmpe?://[^,]+),bitrate:(?P<bitrate>[0-9]+)(?=.*?subtitle=(?P<sub>[^&]*))',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump --swfVfy http://svtplay.se%(swf_url)s -r %(url)s -o %(output_file)s'}],
		[#SVT-play-alternate/flv clip
			{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
				'template'	:	'http://svtplay.se/%(url)s'},
			#{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<path>(t|v)/\d+)',
			#	'template'	:	'http://svtplay.se/popup/minispelare/%(path)s'},
			{	're'		:	r'pathflv=(?P<url>http?://[^&]+)',
				'template'	:	'#\n%(url)s'}],
		[#SVT-play-alternate/flv clip-rtmp
			{	're'		:	r'(http://)?(www\.)?svtplay.se/(?P<url>.+)',
				'template'	:	'http://svtplay.se/%(url)s'},
			{	're'		:	r'(?:name="movie" value="(?P<swf_url>[^"]+)".*?)pathflv=(?P<url>rtmpe?://[^&]+)',
				'template'	:	'#\nrtmpdump -W "http://svtplay.se%(swf_url)s" -r "%(url)s" -o %(output_file)s'}],
		[
			{	'service-name':		'SR',
				're'		:	r'(http://)?(www\.)?sverigesradio.se/(?P<url>.+)',
				'template'	:	'http://sverigesradio.se/%(url)s'},
			{	're'		:	r'<ref href="(?P<url>[^"]+)"',
				'template'	:	'#\n%(url)s'}],
		[
			{	'service-name':		'UR-play',
				're'		:	r'(http://)?(www\.)?urplay.se/(?P<url>.+)',
				'template'	:	'http://urplay.se/%(url)s'},
			{	're'		:	r'file=/(?P<url>[^&]+(?P<ext>mp[34]))(?:.*?captions.file=(?P<sub>[^&]+))?',
				'template'	:	'#subtitles: %(sub)s;\nrtmpdump -r rtmp://streaming.ur.se/ -y %(ext)s:/%(url)s -a ondemand -o %(output_file)s'}],
		[
			{	'service-name':		'TV4-play',
				're'		:	r'(http://)?(www\.)?tv4play.se/.*videoid=(?P<id>\d+).*',
				'template'	:	'http://premium.tv4play.se/api/web/asset/%(id)s/play'},
			{	're'		:	r'(<playbackStatus>(?P<status>\w+).*?)?<bitrate>(?P<bitrate>[0-9]+)</bitrate>.*?(?P<base>rtmpe?://[^<]+).*?(?P<url>mp4:/[^<]+)(?=.*?(?P<sub>http://anytime.tv4.se/multimedia/vman/smiroot/[^<]+))?',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://www.tv4play.se/flash/tv4playflashlets.swf -r %(base)s -y %(url)s -o %(output_file)s'}],
		[
			{	'service-name':		'MTG',
				're'		:	r'(http://)?(www\.)?tv[368]play.se/.*(?:play/(?P<id>\d+)).*',
				'template'	:	'http://viastream.viasat.tv/PlayProduct/%(id)s'},
			{	're'		:	r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>rtmp[^\]]+)',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://flvplayer-viastream-viasat-tv.origin.vss.viasat.tv/play/swf/player110420.swf -r %(url)s -o %(output_file)s'}],
		[#MTG-alternate
			{	're'		:	r'(http://)?(www\.)?tv[368]play.se/.*(?:play/(?P<id>\d+)).*',
				'template'	:	'http://viastream.viasat.tv/PlayProduct/%(id)s'},
			{	're'		:	r'<SamiFile>(?P<sub>[^<]*).*<Video>.*<BitRate>(?P<bitrate>\d+).*?<Url><!\[CDATA\[(?P<url>http[^\]]+)',
				'template'	:	'%(url)s'},
			{	're'		:	r'<Url>(?P<url>[^<]+)',
				'template'	:	'#quality: %(bitrate)s kbps; subtitles: %(sub)s;\nrtmpdump -W http://flvplayer-viastream-viasat-tv.origin.vss.viasat.tv/play/swf/player110420.swf -r %(url)s -o %(output_file)s'}],
		[
			{	'service-name':		'Aftonbladet-TV',
				're'		:	r'(http://)?(www\.)?aftonbladet.se/(?P<url>.+)',
				'template'	:	'http://aftonbladet.se/%(url)s'},
			{	're'		:	'videoUrl:\s"(?P<base>rtmp://(ss11i04.stream.ip-only.net|fl1.c00862.cdn.qbrick.com)/[^/]+/)(?P<url>[^"]+)"',
				'template'	:	'#\nrtmpdump -r %(base)s -y %(url)s -o %(output_file)s'}],
		[
			{
				'service-name':		'Vimeo',
				'user-agent-string':	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36',
				're'		:	r'(http://)?(www\.)?vimeo.com/(?P<url>.+)',
				'template'	:	'http://vimeo.com/%(url)s'},
			{
				'user-agent-string':	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36',
				're'		:	r'"signature":"(?P<sig>[^"]+)".*?timestamp":(?P<time>\d+).*?h264":\["(?P<quality>[^"]+)',
				'template'	:	'http://player.vimeo.com/play_redirect?clip_id=%(url)s&sig=%(sig)s&time=%(time)s&quality=%(quality)s&codecs=H264,VP8,VP6&type=moogaloop_local&embed_location='},
			{
				'user-agent-string':	'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.36 (KHTML, like Gecko) Chrome/13.0.766.0 Safari/534.36',
				're'		:	r'Location: (?P<url>.*?)\n',
				'template'	:	'#quality: %(quality)s;\n%(url)s'}],
		[
			{	'service-name':		'Kanal5-play, Kanal9-play',
				're'		:	r'(http://)?(www\.)?kanal(?P<n>5|9)play.se/(?P<url>.+)',
				'template'	:	'http://kanal%(n)splay.se/%(url)s'},
			{	're'		:	r'@videoPlayer" value="(?P<video_player>[^"]+)"',
				'template'	:	'kanal5://%(video_player)s'},
			{
				're'		:	r'"(?P<height>\d+)x(?P<width>\d+):(?P<URL>[^&]+)&(?P<path>[^"]+)";',
				'template'	:	'#quality: %(height)sx%(width)s;\nrtmpdump --swfVfy "http://admin.brightcove.com/viewer/us1.25.04.01.2011-05-24182704/connection/ExternalConnection_2.swf" -r %(URL)s -y %(path)s -o %(output_file)s'}],
		[
			{	'service-name':		'Axess-TV',
				're'		:	r'(http://)?(www\.)?axess.se/(?P<url>.+)',
				'template'	:	'http://axess.se/%(url)s'},
			{	're'		:	r'url: \'(?P<url>[^\']+)\'.*netConnectionUrl: \'(?P<base>[^\']+)',
				'template'	:	'#\nrtmpdump -r %(base)s -y %(url)s -o %(output_file)s'}]]