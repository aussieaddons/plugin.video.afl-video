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


def make_rounds(params):
    utils.log('Making rounds list...')
    try:
        season = comm.get_seasons(season=params.get('season'))
        rounds = reversed(season.get('rounds'))
        for r in rounds:
            name = r.get('name')
            round_id = r.get('roundId')
            season_id = r.get('seasonId')
            listitem = xbmcgui.ListItem(label=name)
            url = '{0}?name={1}&round_id={2}&season_id={3}'.format(
                sys.argv[0], name, round_id, season_id)

            # Add the item to the list
            ok = xbmcplugin.addDirectoryItem(
                handle=int(sys.argv[1]),
                url=url,
                listitem=listitem,
                isFolder=True,
                totalItems=len(season.get('rounds')))

        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except Exception:
        utils.handle_error('Unable to make round list')
