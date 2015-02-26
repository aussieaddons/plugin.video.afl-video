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
		pDialog.create('AFL Video', 'Getting Round List')
		pDialog.update(50)

		for r in config.ROUNDS_2015:
			listitem = xbmcgui.ListItem(label=r['name'])
			url = "%s?round_id=%s" % (sys.argv[0], r['id'])

			# Add the item to the list
			ok = xbmcplugin.addDirectoryItem(
						handle = int(sys.argv[1]),
						url = url,
						listitem = listitem,
						isFolder = True,
						totalItems = len(config.ROUNDS_2015)
					)

		# send notification we're finished, successfully or unsuccessfully
		xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to fetch round list")
		d.ok(*message)
		utils.log_error();
