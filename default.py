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
