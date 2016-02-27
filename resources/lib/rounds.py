#
#    AFL Video Kodi Add-on
#    Copyright (C) 2016 Andy Botting
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
#    along with this add-on. If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import config
import utils
import xbmc
import xbmcgui
import xbmcplugin


def make_rounds(season=2016):
    try:
        # ROUNDS_2016 variable from config
        rounds_config = getattr(config, 'ROUNDS_'+season)

        for r in rounds_config:
            listitem = xbmcgui.ListItem(label=r['name'])
            url = "%s?round_id=%s" % (sys.argv[0], r['id'])

            # Add the item to the list
            ok = xbmcplugin.addDirectoryItem(
                        handle=int(sys.argv[1]),
                        url=url,
                        listitem=listitem,
                        isFolder=True,
                        totalItems=len(rounds_config))

        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except:
        utils.handle_error('Unable to fetch round list')
