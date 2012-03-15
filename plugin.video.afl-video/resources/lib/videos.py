import sys
import config
import utils
import classes

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass

from pyamf.remoting.client import RemotingService

def parse_video(video_item):
	v = video_item['content']
	new_video = classes.Video()
	new_video.id = v['contentId']
	new_video.title = v['title']
	new_video.description = v['description']
	new_video.duration = v['duration']
	new_video.thumbnail = v['imageUrl']
	return new_video


def get_videos(channel_id):
	videos = []
	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('Miscellaneous')
	params = {
		'navId': channel_id, 
		'startRecord': '0', 
		'howMany': '50', 
		'platformId': '1', 
		'phpFunction': 'getClipList', 
		'asFunction': 'publishClipList'
	}
	
	videos_list = service.getClipList(params)
	if videos_list:
		for video_item in videos_list[0]['items']:
			video = parse_video(video_item)
			videos.append(video)
	else:
		print "ERROR: Video list returned no results."

	return videos


def make_list(url):
	params = utils.get_url(url)
	channel = params['channel']

	utils.log("Fetching video list for channel %s..." % channel)

	# Show a dialog
	pDialog = xbmcgui.DialogProgress()
	pDialog.create(config.NAME, 'Fetching video list...')

	videos = get_videos(channel)

	utils.log("Found %s videos" % len(videos))

	# fill media list
	ok = fill_video_list(videos)

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_video_list(videos):
	try:
		ok = True
		for v in videos:
			listitem = xbmcgui.ListItem(label=v.get_title(), iconImage=v.get_thumbnail(), thumbnailImage=v.get_thumbnail())
			listitem.setInfo('video', v.get_xbmc_list_item())
	
			# Build the URL for the program, including the list_info
			url = "%s?%s" % (sys.argv[0], v.make_xbmc_url())

			# Add the program item to the list
			ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
	except:
		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % ( sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
		ok = False
	return ok

