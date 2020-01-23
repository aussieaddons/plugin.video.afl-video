import os
import sys
import xbmcaddon

from aussieaddonscommon import utils

# Add our resources/lib to the python path
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

import index  # noqa: E402
import ooyalahelper  # noqa: E402
import play  # noqa: E402
import rounds  # noqa: E402
import teams  # noqa: E402
import videos  # noqa: E402

# Print our platform/version debugging information
utils.log_kodi_platform_version()

if __name__ == "__main__":
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
            except Exception as e:
                utils.dialog_message(
                    "Can't open inputstream.adaptive settings")
