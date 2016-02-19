#
#	 AFL Video XBMC Plugin
#	 Copyright (C) 2012 Andy Botting
#
#	 AFL Video is free software: you can redistribute it and/or modify
#	 it under the terms of the GNU General Public License as published by
#	 the Free Software Foundation, either version 3 of the License, or
#	 (at your option) any later version.
#
#	 AFL Video is distributed in the hope that it will be useful,
#	 but WITHOUT ANY WARRANTY; without even the implied warranty of
#	 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	 GNU General Public License for more details.
#
#	 You should have received a copy of the GNU General Public License
#	 along with AFL Video.  If not, see <http://www.gnu.org/licenses/>.
#

import sys
import config
import utils
import classes
import comm

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass

def make_list(round_id, match_id):

	__addon__ = xbmcaddon.Addon()
	quality = __addon__.getSetting('QUALITY')

	utils.log("Fetching video list for %s..." % match_id)
	try:
		# fill media list
		videos = comm.get_match_video(round_id, match_id, quality)
		if videos:
			ok = True
			for v in videos:
				listitem = xbmcgui.ListItem(label=v['name'])
				# I think this might help prevent the stream from closing early
				url = v['url'] + '?start=0'
				xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)
			xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
		else:
			d = xbmcgui.Dialog()
			msg = utils.dialog_message("No videos found. Replays are only available 24-48 hours after match has been played. Please try again later.")
			d.ok(*msg)
	except:
		utils.handle_error('Unable to fetch program list')
