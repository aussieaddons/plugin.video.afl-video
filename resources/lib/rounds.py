import comm
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
