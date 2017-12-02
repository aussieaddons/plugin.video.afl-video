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

import comm
import config
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_list():
    try:
        for category in config.CATEGORIES:
            url = "%s?category=%s" % (sys.argv[0], category)
            listitem = xbmcgui.ListItem(category)

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True,
                                             totalItems=len(config.CATEGORIES))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except Exception:
        utils.handle_error('Unable build video category list')


def make_seasons_list():
    try:
        seasons = comm.get_seasons()
        sorted_seasons = sorted(
            seasons, key=lambda x: x.get('name'), reverse=True)
        for season in sorted_seasons:
            id = season.get('id')
            current_round = season.get('currentRoundId')
            name = season.get('name')
            url = "{0}?season={1}&current_round={2}&name={3}".format(
                sys.argv[0], id, current_round, name)
            listitem = xbmcgui.ListItem(name)

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True,
                                             totalItems=len(seasons))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except Exception:
        utils.handle_error('Unable build seasons list')
