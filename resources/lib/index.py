import sys

from aussieaddonscommon import utils

from resources.lib import comm
from resources.lib import config

import xbmcgui

import xbmcplugin


def make_list():
    try:
        for category in config.CATEGORIES:
            url = '{0}?category={1}'.format(sys.argv[0], category)
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
