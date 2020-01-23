import sys

from aussieaddonscommon import utils

from resources.lib import index
from resources.lib import ooyalahelper
from resources.lib import play
from resources.lib import rounds
from resources.lib import teams
from resources.lib import videos

import xbmcaddon

# Print our platform/version debugging information
utils.log_kodi_platform_version()


def main():
    params_str = sys.argv[2]
    params = utils.get_url(params_str)
    utils.log('Loading with params: {0}'.format(params))

    if len(params) == 0:
        index.make_list()
    elif 'category' in params:
        if params['category'] == 'Settings':
            xbmcaddon.Addon().openSettings()
        elif params['category'] == 'Team Video':
            teams.make_list()
        elif params['category'] == 'All Match Replays':
            index.make_seasons_list()
        else:
            videos.make_list(params)
    elif 'season' in params:
        rounds.make_rounds(params)
    elif 'team' in params:
        videos.make_list(params)
    elif 'round_id' in params:
        videos.make_list(params)
    elif 'title' in params:
        play.play(params_str)
    elif 'action' in params:
        if params['action'] == 'cleartoken':
            ooyalahelper.clear_token()
        elif params['action'] == 'sendreport':
            utils.user_report()
        elif params['action'] == 'iap_help':
            ooyalahelper.iap_help()
        elif params['action'] == 'open_ia_settings':
            try:
                import drmhelper
                if drmhelper.check_inputstream(drm=False):
                    ia = drmhelper.get_addon()
                    ia.openSettings()
                else:
                    utils.dialog_message(
                        "Can't open inputstream.adaptive settings")
            except Exception:
                utils.dialog_message(
                    "Can't open inputstream.adaptive settings")


if __name__ == "__main__":
    main()
