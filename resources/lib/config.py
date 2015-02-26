#
#    AFL Video XBMC Plugin
#    Copyright (C) 2012 Andy Botting
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
#    along with AFL Video.  If not, see <http://www.gnu.org/licenses/>.
#

NAME = 'AFL Video'

# Video quality static definitions with match the setings.xml
QUAL_LOW = '0'
QUAL_MED = '1'
QUAL_HIGH = '2'

# These values match the bitrate given in the video data
VIDEO_QUALITY = { '0': 172,
                  '1': 1024,
                  '2': 2048  }

# These are the strings used for selecting quality via the smart replay system.
REPLAY_QUALITY = { '0': 'low',
                   '1': 'med',
                   '2': 'high'  }

# Round URL, which lists the games of the round if they've had their Videos uploaded
# This URL can also take a 'Round ID' added to the end (e.g CD_R201301401)
ROUND_URL = 'http://www.afl.com.au/api/gas/afl/roundVideo'

# This URL returns a token if POST'ed to. The token is required in the header to any
# reqeusts against the API
TOKEN_URL = 'http://api.afl.com.au/cfs/afl/WMCTok'

# The API URL for listing videos
VIDEO_LIST_URL = 'http://api.afl.com.au/cfs/afl/video'

# Categories existing on the new content system
CATEGORIES = [
	'Match Replays 2015',
	'Match Replays 2014',
	'Match Replays 2013',
	'Club Video',
	'Settings'
]

# Standard Bigpond Sport/AFL channels
# Channel number was discovered from http://bigpondvideo.com/
# and using a web proxy, extract the AMF data when clicking each channel
# to find its 'NavID' 
# channel value matches with the teams list in the settings.xml
# NOTE: Now only used for 'Club Video'. Everything else moved to new API feed
CHANNELS = []

# Channel is used for Bigpond Video and Squad is used in Round XML
# http://www.afl.com.au/api/gas/afl/squad
TEAMS = [
	{'id': '1',  'name': 'Adelaide',            'squad': '10',   'channel': '14',   'thumb': 'adel.gif' },
	{'id': '2',  'name': 'Brisbane',            'squad': '20',   'channel': '22',   'thumb': 'bris.gif' },
	{'id': '3',  'name': 'Carlton',             'squad': '30',   'channel': '30',   'thumb': 'carl.gif' },
	{'id': '4',  'name': 'Collingwood',         'squad': '40',   'channel': '38',   'thumb': 'coll.gif' },
	{'id': '5',  'name': 'Essendon',            'squad': '50',   'channel': '46',   'thumb': 'ess.gif'  },
	{'id': '6',  'name': 'Fremantle',           'squad': '60',   'channel': '54',   'thumb': 'frem.gif' },
	{'id': '7',  'name': 'Gold Coast',          'squad': '1000', 'channel': '2734', 'thumb': 'gcfc.gif' },
	{'id': '8',  'name': 'Geelong',             'squad': '70',   'channel': '62',   'thumb': 'geel.gif' },
	{'id': '9',  'name': 'Greater West Sydney', 'squad': '1010', 'channel': '3798', 'thumb': 'gws.gif'  },
	{'id': '10', 'name': 'Hawthorn',            'squad': '80',   'channel': '70',   'thumb': 'haw.gif'  },
	{'id': '11', 'name': 'Melbourne',           'squad': '90',   'channel': '86',   'thumb': 'melb.gif' },
	{'id': '12', 'name': 'North Melbourne',     'squad': '100',  'channel': '78',   'thumb': 'nmfc.gif' },
	{'id': '13', 'name': 'Port Adelaide',       'squad': '110',  'channel': '94',   'thumb': 'port.gif' },
	{'id': '14', 'name': 'Richmond',            'squad': '120',  'channel': '102',  'thumb': 'rich.gif' },
	{'id': '15', 'name': 'St. Kilda',           'squad': '130',  'channel': '110',  'thumb': 'stk.gif'  },
	{'id': '16', 'name': 'Sydney',              'squad': '160',  'channel': '118',  'thumb': 'syd.gif'  },
	{'id': '17', 'name': 'West Coast',          'squad': '150',  'channel': '126',  'thumb': 'wce.gif'  },
	{'id': '18', 'name': 'Western Bulldogs',    'squad': '140',  'channel': '134',  'thumb': 'wb.gif'   },
]

ROUNDS_2015 = [
	{'id': 'latest',        'name': 'Current Round'},
	{'id': 'CD_R201510101', 'name': 'NAB Challenge'},
	{'id': 'CD_R201501401', 'name': 'Round 1'},
	{'id': 'CD_R201501402', 'name': 'Round 2'},
	{'id': 'CD_R201501403', 'name': 'Round 3'},
	{'id': 'CD_R201501404', 'name': 'Round 4'},
	{'id': 'CD_R201501405', 'name': 'Round 5'},
	{'id': 'CD_R201501406', 'name': 'Round 6'},
	{'id': 'CD_R201501407', 'name': 'Round 7'},
	{'id': 'CD_R201501408', 'name': 'Round 8'},
	{'id': 'CD_R201501409', 'name': 'Round 9'},
	{'id': 'CD_R201501410', 'name': 'Round 10'},
	{'id': 'CD_R201501411', 'name': 'Round 11'},
	{'id': 'CD_R201501412', 'name': 'Round 12'},
	{'id': 'CD_R201501413', 'name': 'Round 13'},
	{'id': 'CD_R201501414', 'name': 'Round 14'},
	{'id': 'CD_R201501415', 'name': 'Round 15'},
	{'id': 'CD_R201501416', 'name': 'Round 16'},
	{'id': 'CD_R201501417', 'name': 'Round 17'},
	{'id': 'CD_R201501418', 'name': 'Round 18'},
	{'id': 'CD_R201501419', 'name': 'Round 19'},
	{'id': 'CD_R201501420', 'name': 'Round 20'},
	{'id': 'CD_R201501421', 'name': 'Round 21'},
	{'id': 'CD_R201501422', 'name': 'Round 22'},
	{'id': 'CD_R201501423', 'name': 'Round 23'},
	{'id': 'CD_R201501424', 'name': 'Finals Week 1'},
	{'id': 'CD_R201501425', 'name': 'Finals Week 2'},
	{'id': 'CD_R201501426', 'name': 'Finals Week 3'},
	{'id': 'CD_R201501427', 'name': 'Grand Final'},
]

ROUNDS_2014 = [
	{'id': 'CD_R201410101', 'name': 'NAB Challenge'},
	{'id': 'CD_R201401401', 'name': 'Round 1'},
	{'id': 'CD_R201401402', 'name': 'Round 2'},
	{'id': 'CD_R201401403', 'name': 'Round 3'},
	{'id': 'CD_R201401404', 'name': 'Round 4'},
	{'id': 'CD_R201401405', 'name': 'Round 5'},
	{'id': 'CD_R201401406', 'name': 'Round 6'},
	{'id': 'CD_R201401407', 'name': 'Round 7'},
	{'id': 'CD_R201401408', 'name': 'Round 8'},
	{'id': 'CD_R201401409', 'name': 'Round 9'},
	{'id': 'CD_R201401410', 'name': 'Round 10'},
	{'id': 'CD_R201401411', 'name': 'Round 11'},
	{'id': 'CD_R201401412', 'name': 'Round 12'},
	{'id': 'CD_R201401413', 'name': 'Round 13'},
	{'id': 'CD_R201401414', 'name': 'Round 14'},
	{'id': 'CD_R201401415', 'name': 'Round 15'},
	{'id': 'CD_R201401416', 'name': 'Round 16'},
	{'id': 'CD_R201401417', 'name': 'Round 17'},
	{'id': 'CD_R201401418', 'name': 'Round 18'},
	{'id': 'CD_R201401419', 'name': 'Round 19'},
	{'id': 'CD_R201401420', 'name': 'Round 20'},
	{'id': 'CD_R201401421', 'name': 'Round 21'},
	{'id': 'CD_R201401422', 'name': 'Round 22'},
	{'id': 'CD_R201401423', 'name': 'Round 23'},
	{'id': 'CD_R201401424', 'name': 'Finals Week 1'},
	{'id': 'CD_R201401425', 'name': 'Finals Week 2'},
	{'id': 'CD_R201401426', 'name': 'Finals Week 3'},
	{'id': 'CD_R201401427', 'name': 'Grand Final'},
]

ROUNDS_2013 = [
        {'id': 'CD_R201301401', 'name': 'Round 1'},
        {'id': 'CD_R201301402', 'name': 'Round 2'},
        {'id': 'CD_R201301403', 'name': 'Round 3'},
        {'id': 'CD_R201301404', 'name': 'Round 4'},
        {'id': 'CD_R201301405', 'name': 'Round 5'},
        {'id': 'CD_R201301406', 'name': 'Round 6'},
        {'id': 'CD_R201301407', 'name': 'Round 7'},
        {'id': 'CD_R201301408', 'name': 'Round 8'},
        {'id': 'CD_R201301409', 'name': 'Round 9'},
        {'id': 'CD_R201301410', 'name': 'Round 10'},
        {'id': 'CD_R201301411', 'name': 'Round 11'},
        {'id': 'CD_R201301412', 'name': 'Round 12'},
        {'id': 'CD_R201301413', 'name': 'Round 13'},
        {'id': 'CD_R201301414', 'name': 'Round 14'},
        {'id': 'CD_R201301415', 'name': 'Round 15'},
        {'id': 'CD_R201301416', 'name': 'Round 16'},
        {'id': 'CD_R201301417', 'name': 'Round 17'},
        {'id': 'CD_R201301418', 'name': 'Round 18'},
        {'id': 'CD_R201301419', 'name': 'Round 19'},
        {'id': 'CD_R201301420', 'name': 'Round 20'},
        {'id': 'CD_R201301421', 'name': 'Round 21'},
        {'id': 'CD_R201301422', 'name': 'Round 22'},
        {'id': 'CD_R201301423', 'name': 'Round 23'},
        {'id': 'CD_R201301424', 'name': 'Finals Week 1'},
        {'id': 'CD_R201301425', 'name': 'Finals Week 2'},
        {'id': 'CD_R201301426', 'name': 'Finals Week 3'},
        {'id': 'CD_R201301427', 'name': 'Grand Final'},
]
