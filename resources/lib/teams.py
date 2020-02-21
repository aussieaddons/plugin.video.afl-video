import os
import sys

from aussieaddonscommon import utils

from resources.lib import config

import xbmcgui

import xbmcplugin


def make_list():
    try:
        for t in config.TEAMS:
            # Add our resources/lib to the python path
            try:
                current_dir = os.path.dirname(os.path.abspath(__file__))
            except Exception:
                current_dir = os.getcwd()

            thumb = os.path.join(current_dir, "..", "..", "resources",
                                     "img", t['thumb'])
            listitem = xbmcgui.ListItem(label=t['name'])
            listitem.setArt({'icon': thumb, 'thumb': thumb})
            url = "%s?team=%s" % (sys.argv[0], t['team_id'])

            # Add the item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True,
                                             totalItems=len(config.TEAMS))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch video list')
