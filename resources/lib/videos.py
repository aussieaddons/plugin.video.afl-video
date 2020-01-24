import sys

from aussieaddonscommon import utils
from aussieaddonscommon.exceptions import AussieAddonsException

from resources.lib import comm
from resources.lib import config

import xbmcgui

import xbmcplugin


def make_list(params):
    utils.log('Making video list...')
    cache = True
    try:
        if 'team' in params:
            videos = comm.get_team_videos(params.get('team'))
        elif 'round_id' in params:
            videos = comm.get_round_videos(params.get('round_id'))
        elif params.get('category') == 'Live Matches':
            videos = comm.get_live_videos()
            cache = False
        elif params.get('category') == 'AFLW':
            videos = comm.get_aflw_videos()
        else:
            try:
                category = config.CATEGORY_LOOKUP[params.get('category')]
            except KeyError as e:
                xbmcgui.Dialog().ok(
                    'Outdated Favourites Link',
                    'The Kodi Favourite item being accessed was created with '
                    'an earlier version of the AFL Video add-on and is no '
                    'longer compatible. Please remove this link and update '
                    'with a new one.')
                raise AussieAddonsException(e)
            videos = comm.get_category_videos(category)

        ok = True
        for v in videos:
            listitem = xbmcgui.ListItem(label=v.get_title(),
                                        thumbnailImage=v.get_thumbnail())
            listitem.setInfo('video', v.get_kodi_list_item())
            listitem.addStreamInfo('video', v.get_kodi_stream_info())
            if not v.isdummy:
                listitem.setProperty('IsPlayable', 'true')

            # Build the URL for the program, including the list_info
            url = "%s?%s" % (sys.argv[0], v.make_kodi_url())

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),
                                  succeeded=ok,
                                  cacheToDisc=cache)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch video list')
