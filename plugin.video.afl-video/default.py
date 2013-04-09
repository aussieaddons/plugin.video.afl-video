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

try:
	import xbmc, xbmcgui, xbmcplugin, xbmcaddon
except ImportError:
	pass

# Add our resources/lib to the python path
try:
	current_dir = os.path.dirname(os.path.abspath(__file__))
except:
	current_dir = os.getcwd()

sys.path.append( os.path.join( current_dir, "resources", "lib" ) )

import utils, config, comm, index, teams, videos, play, pyamf

utils.log('Initialised')

__addon__ = xbmcaddon.Addon()

if __name__ == "__main__" :
	params_str = sys.argv[2]
	params = utils.get_url(params_str)

	if (len(params) == 0):
		index.make_list()
	else:
		if params.has_key('channel'):
			if params['channel'] == 'teams':
				teams.make_list()
			elif params['channel'] == 'settings':
				__addon__.openSettings()
			else:
				videos.make_list(params_str)

		elif params.has_key("title"):
			play.play(params_str)

