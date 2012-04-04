import os
import sys
import config
import utils

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

def make_list():
	#params = utils.get_url(url)	

	try:
		# Show a dialog
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('AFL Video', 'Getting Episode List')
		pDialog.update(50)

		teams = config.TEAMS

		# fill media list
		ok = fill_team_list(teams)
	except:
		# oops print error message
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_team_list(teams):

	try:	
		ok = True

		for t in teams:
			# Thumbnail

			# Add our resources/lib to the python path
			try:
				current_dir = os.path.dirname(os.path.abspath(__file__))
			except:
				current_dir = os.getcwd()

			thumbnail = os.path.join(current_dir, "..", "..", "resources", "img", t['thumb'])
			utils.log("Thumbnail: %s" % thumbnail)
			listitem = xbmcgui.ListItem(label=t['name'], iconImage=thumbnail, thumbnailImage=thumbnail)
			url = "%s?channel=%s" % (sys.argv[0], t['id'])

			# Add the item to the list
			ok = xbmcplugin.addDirectoryItem(
						handle = int(sys.argv[1]),
						url = url,
						listitem = listitem,
						isFolder = True,
						totalItems = len(teams)
					)
					

		xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
	except:
		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % ( sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ], )
		ok = False

	return ok
