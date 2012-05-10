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

# main imports
import sys, os, re, urllib2, urllib
import config
import utils

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass 

def make_list():

	try:
		items = []

		__addon__ = xbmcaddon.Addon()
		favourite_team =  __addon__.getSetting('TEAM')

		if favourite_team > 0:
			for team in config.TEAMS:
				if favourite_team == team['id']:
					items.append({'name': team['name'], 'channel': team['channel']})


		# Add the other feeds listed in the config file
		for channel in config.CHANNELS:
			items.append({'name': channel['name'], 'channel': channel['channel']})

		items.append({'name': 'Settings', 'channel': 'settings'})

		# fill media list
		ok = fill_media_list(items)
	except:
		# oops print error message
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[2].tb_frame.f_code.co_name, sys.exc_info()[2].tb_lineno, sys.exc_info()[1])
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_media_list(items):

	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for i in items:
			url = "%s?channel=%s" % (sys.argv[0], i['channel'])
			#thumbnail = get_thumbnail(c.channel)
			icon = "defaultfolder.png"
			listitem = xbmcgui.ListItem(i['name'], iconImage=icon)
			#listitem.setInfo('video',{'episode':s.get_num_episodes()})
			# add the item to the media list

			ok = xbmcplugin.addDirectoryItem(
						handle=int(sys.argv[1]), 
						url=url, 
						listitem=listitem, 
						isFolder=True, 
						totalItems=len(config.CHANNELS) + 1
					)

			# if user cancels, call raise to exit loop
			if (not ok): 
				raise

		#xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		d.ok('AFL Video Error', 'AFL Video encountered an error:', '  %s (%d) - %s' % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ]) )

		# user cancelled dialog or an error occurred
		print "ERROR: %s (%d) - %s" % (sys.exc_info()[ 2 ].tb_frame.f_code.co_name, sys.exc_info()[ 2 ].tb_lineno, sys.exc_info()[ 1 ],)
		ok = False

	return ok
