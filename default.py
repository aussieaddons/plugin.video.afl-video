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

# Add our resources/lib to the python path
try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
except:
    current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, "resources", "lib"))

import utils
import config
import comm
import index
import teams
import rounds
import matches
import videos
import play_replay
import play

utils.log('Initialised')

__addon__ = xbmcaddon.Addon()

if __name__ == "__main__":
    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if (len(params) == 0):
        index.make_list()
    else:
        if 'channel' in params:
            videos.make_list(params_str)

        elif 'category' in params:
            # Settings
            if params['category'] == 'Settings':
                __addon__.openSettings()

            # Team video list -- disabled until moved to new API
            # elif params['category'] == 'Club Video':
            #     teams.make_list()

            # Match replay round list
            elif params['category'].startswith('Match Replays'):
                # Pull season out from end of category name
                season = params['category'].split()[-1]
                rounds.make_rounds(season)

            else:
                videos.make_list(params_str)

        # List of videos (quarters) for a match
        elif 'match_id' in params:
            play_replay.make_list(params['round_id'], params['match_id'])

        # Match list for a round
        elif 'round_id' in params:
            matches.make_list(params['round_id'])

        elif 'title' in params:
            play.play(params_str)
