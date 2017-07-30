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
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except Exception:
    current_dir = os.getcwd()
sys.path.append(os.path.join(current_dir, "resources", "lib"))

import index  # noqa: E402
import matches  # noqa: E402
import ooyalahelper  # noqa: E402
import play  # noqa: E402
import play_replay  # noqa: E402
import rounds  # noqa: E402
import teams  # noqa: E402
import videos  # noqa: E402

# Print our platform/version debugging information
utils.log_xbmc_platform_version()

if __name__ == "__main__":
    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if (len(params) == 0):
        index.make_list()
    else:
        if 'category' in params:
            if params['category'] == 'Settings':
                xbmcaddon.Addon().openSettings()
            elif params['category'] == 'Team Video':
                teams.make_list()
            elif params['category'].startswith('Match Replays'):
                # Pull season out from end of category name
                season = params['category'].split()[-1]
                rounds.make_rounds(season)
            else:
                videos.make_list(params_str)
        elif 'team' in params:
            videos.make_list(params_str)
        elif 'match_id' in params:
            # List of videos (quarters) for a match
            play_replay.make_list(params['round_id'], params['match_id'])
        elif 'round_id' in params:
            # Match list for a round
            matches.make_list(params['round_id'])
        elif 'title' in params:
            play.play(params_str)
        elif 'action' in params:
            if params['action'] == 'cleartoken':
                ooyalahelper.clear_token()
