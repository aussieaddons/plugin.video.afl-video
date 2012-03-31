"""
	Plugin for streaming content from AFL.com.au
"""

import os
import sys

# Add our resources/lib to the python path
try:
	current_dir = os.path.dirname(os.path.abspath(__file__))
except:
	current_dir = os.getcwd()

sys.path.append( os.path.join( current_dir, "resources", "lib" ) )

import utils, config, index, teams, videos, play, pyamf

utils.log('Initialised')

if __name__ == "__main__" :
	params_str = sys.argv[2]
	params = utils.get_url(params_str)

	if (len(params) == 0):
		index.make_list()
	else:
		if params.has_key('channel'):
			if params['channel'] == 'teams':
				teams.make_list()
			else:
				videos.make_list(params_str)

		elif params.has_key("title"):
			play.play(params_str)

