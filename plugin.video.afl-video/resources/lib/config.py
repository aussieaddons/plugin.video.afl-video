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
VERSION = '0.6'

# Video quality static definitions with match the setings.xml
QUAL_LOW = '0'
QUAL_MED = '1'
QUAL_HIGH = '2'

# Standard Bigpond Sport/AFL channels
# Channel number was discovered from http://bigpondvideo.com/
# and using a web proxy, extract the AMF data when clicking each channel
# to find its 'NavID' 
# channel value matches with the teams list in the settings.xml
CHANNELS = [
	{ 'name': 'Teams',       'channel': 'teams' },
	{ 'name': 'Matches',     'channel': '9' },
	{ 'name': 'Newsdesk',    'channel': '10' },
	{ 'name': 'Highlights',  'channel': '11' },
	{ 'name': 'Panel Shows', 'channel': '13' },
]

TEAMS = [
	{'id': '1',  'name': 'Adelaide',            'channel': '14',   'thumb': 'adel.gif' },
	{'id': '2',  'name': 'Brisbane',            'channel': '22',   'thumb': 'bris.gif' },
	{'id': '3',  'name': 'Carlton',             'channel': '30',   'thumb': 'carl.gif' },
	{'id': '4',  'name': 'Collingwood',         'channel': '38',   'thumb': 'coll.gif' },
	{'id': '5',  'name': 'Essendon',            'channel': '46',   'thumb': 'ess.gif'  },
	{'id': '6',  'name': 'Fremantle',           'channel': '54',   'thumb': 'frem.gif' },
	{'id': '7',  'name': 'Gold Coast',          'channel': '2734', 'thumb': 'gcfc.gif' },
	{'id': '8',  'name': 'Geelong',             'channel': '62',   'thumb': 'geel.gif' },
	{'id': '9',  'name': 'Greater West Sydney', 'channel': '3798', 'thumb': 'gws.gif'  },
	{'id': '10', 'name': 'Hawthorn',            'channel': '70',   'thumb': 'haw.gif'  },
	{'id': '11', 'name': 'Melbourne',           'channel': '86',   'thumb': 'melb.gif' },
	{'id': '12', 'name': 'North Melbourne',     'channel': '78',   'thumb': 'nmfc.gif' },
	{'id': '13', 'name': 'Port Adelaide',       'channel': '94',   'thumb': 'port.gif' },
	{'id': '14', 'name': 'Richmond',            'channel': '102',  'thumb': 'rich.gif' },
	{'id': '15', 'name': 'St. Kilda',           'channel': '110',  'thumb': 'stk.gif'  },
	{'id': '16', 'name': 'Sydney',              'channel': '118',  'thumb': 'syd.gif'  },
	{'id': '17', 'name': 'West Coast',          'channel': '126',  'thumb': 'wce.gif'  },
	{'id': '18', 'name': 'Western Bulldogs',    'channel': '134',  'thumb': 'wb.gif'   },
]

