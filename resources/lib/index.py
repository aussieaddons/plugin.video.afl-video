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

import sys
import config
import utils
import xbmcaddon
import xbmcgui
import xbmcplugin


def make_list():
    try:
        # Disabled until team channels has been moved to new API
        # items = []
        # __addon__ = xbmcaddon.Addon()
        # favourite_team =  __addon__.getSetting('TEAM')
        # if favourite_team > 0:
        #     for team in config.TEAMS:
        #         if favourite_team == team['id']:
        #             items.append({'name': team['name'],
        #                           'channel': team['channel']})
        #
        # enumerate through the list of categories and add the item
        # to the media list

        for category in config.CATEGORIES:
            url = "%s?category=%s" % (sys.argv[0], category)
            listitem = xbmcgui.ListItem(category)

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(
                        handle=int(sys.argv[1]),
                        url=url,
                        listitem=listitem,
                        isFolder=True,
                        totalItems=len(config.CATEGORIES)
                    )

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except:
        utils.handle_error('Unable build video category list')
