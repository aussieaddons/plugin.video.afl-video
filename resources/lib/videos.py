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

import sys
import config
import utils
import classes
import comm

try:
    import xbmc, xbmcgui, xbmcplugin
except ImportError:
    pass

def make_list(url):

    try:
        params = utils.get_url(url)

        # Old-style video index (used for team video)
        if params.has_key('channel'):
            channel = params['channel']
            videos = comm.get_videos(channel)
        # New-style video index
        elif params.has_key('category'):
            category = params['category']
            videos = comm.get_videos_new(category)

        utils.log("Found %s videos" % len(videos))

        # fill media list
        ok = True
        for v in videos:
            listitem = xbmcgui.ListItem(label=v.get_title(), thumbnailImage=v.get_thumbnail())
            listitem.setInfo('video', v.get_xbmc_list_item())
            listitem.addStreamInfo('video', v.get_xbmc_stream_info())

            # Build the URL for the program, including the list_info
            url = "%s?%s" % (sys.argv[0], v.make_xbmc_url())

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        utils.handle_error('Unable to fetch video list')
