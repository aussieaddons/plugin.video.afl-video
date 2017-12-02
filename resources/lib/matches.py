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
import sys
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def make_list(params):
    utils.log("Fetching match list for round %s..." % params['round_id'])
    try:
        matches = comm.get_round(params)
        utils.log("Found %s matches" % len(matches))

        ok = True
        for m in matches:
            listitem = xbmcgui.ListItem(label=m.title)
            url = "%s?title=%s&ooyalaid=%s&subscription_required=True" % (sys.argv[0],
                                                  m.title,
                                                  m.id)

            # Add the item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True,
                                             totalItems=len(matches))

        # send notification we're finished, successfully or unsuccessfully
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except Exception:
        utils.handle_error('Unable to fetch match list')
