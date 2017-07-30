#
#     AFL Video Kodi Add-on
#     Copyright (C) 2016 Andy Botting
#
#     AFL Video is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     AFL Video is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this add-on. If not, see <http://www.gnu.org/licenses/>.
#

import comm
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


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
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                            url=url,
                                            listitem=listitem,
                                            isFolder=False)
            xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        else:
            utils.dialog_message('No videos found. Replays are only available '
                                 '24 hours after match has been played.'
                                 'Please try again later.')
    except Exception:
        utils.handle_error('Unable to play replay')
