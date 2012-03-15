import sys
import re

import classes
import config
import utils

from pyamf.remoting.client import RemotingService

import xbmc, xbmcgui, xbmcplugin, xbmcaddon

__addon__ = xbmcaddon.Addon()

def get_url(video_id):
	utils.log("Fetching video URL for content ID %s..." % video_id)

	client = RemotingService('http://afl.bigpondvideo.com/App/AmfPhp/gateway.php')
	service = client.getService('SEOPlayer')
	#video_high_qual = service.getMediaURL({'cid': video_id})
	video_url = service.getMediaURL({'cid': video_id})
	#video_low_qual = re.sub("2[mM][bB]{,1}.mp4", "172K.mp4", video_high_qual)
	#video_med_qual = re.sub("2[mM][bB]{,1}.mp4", "1M.mp4", video_high_qual)

	#quality =  __addon__.getSetting('quality')
	#video_url = video_high_qual

	utils.log("Video URL found %s" % video_url)
	return video_url

def play(url):
	v = classes.Video()
	v.parse_xbmc_url(url)

	# Show a dialog
	pDialog = xbmcgui.DialogProgress()
	pDialog.create(config.NAME, 'Starting video...')

	try:
		video_url = get_url(v.id)	
		listitem = xbmcgui.ListItem(label=v.get_title(), iconImage=v.get_thumbnail(), thumbnailImage=v.get_thumbnail())
		listitem.setInfo('video', v.get_xbmc_list_item())
	
		xbmc.Player().play(video_url, listitem)
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('Error', 'Encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )
		return None
		print "ERROR: %s (%d) - %s" % ( sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
