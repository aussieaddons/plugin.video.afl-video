#
#    AFL Video XBMC Plugin
#    Copyright (C) 2012 Andy Botting
#
#    AFL Video is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    AFL Video is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with AFL Video.  If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import config
import utils

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

def make_list():
	try:
		# Show a dialog
		pDialog = xbmcgui.DialogProgress()
		pDialog.create('AFL Video', 'Getting Team List')
		pDialog.update(50)

		for t in config.TEAMS:
			# Add our resources/lib to the python path
			try:
				current_dir = os.path.dirname(os.path.abspath(__file__))
			except:
				current_dir = os.getcwd()

			thumbnail = os.path.join(current_dir, "..", "..", "resources", "img", t['thumb'])
			listitem = xbmcgui.ListItem(label=t['name'], iconImage=thumbnail, thumbnailImage=thumbnail)
			url = "%s?channel=%s" % (sys.argv[0], t['channel'])

			# Add the item to the list
			ok = xbmcplugin.addDirectoryItem(
						handle = int(sys.argv[1]),
						url = url,
						listitem = listitem,
						isFolder = True,
						totalItems = len(config.TEAMS)
					)
					

		xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		msg = utils.dialog_error("Unable to fetch video list")
		d.ok(*msg)
		utils.log_error();

