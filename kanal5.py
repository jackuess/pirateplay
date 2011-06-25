import httplib
from pyamf import remoting

def get_kanal5(video_player):
	player_id = 811317479001
	publisher_id = 22710239001
	const = '9f79dd85c3703b8674de883265d8c9e606360c2e'

	env = remoting.Envelope(amfVersion=3)
	env.bodies.append(
		(
			"/1", 
			remoting.Request(
				target="com.brightcove.player.runtime.PlayerMediaFacade.findMediaById", 
				body=[const, player_id, video_player, publisher_id],
				envelope=env
			)
		)
	)
	env = str(remoting.encode(env).read())

	conn = httplib.HTTPConnection("c.brightcove.com")
	conn.request("POST", "/services/messagebroker/amf?playerKey=AQ~~,AAAABUmivxk~,SnCsFJuhbr0vfwrPJJSL03znlhz-e9bk", env, {'content-type': 'application/x-amf'})
	response = conn.getresponse().read()
	rtmp = ''
	for rendition in remoting.decode(response).bodies[0][1].body['renditions']:
		rtmp += '"%sx%s:%s";' % (rendition['frameWidth'], rendition['frameHeight'], rendition['defaultURL'])
	return rtmp