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
VERSION = '0.5'

# Video quality
QUAL_LOW = 0
QUAL_MED = 1
QUAL_HIGH = 2

CHANNELS = [
	{ 'name': 'Teams',       'id': 'teams' },
	{ 'name': 'Matches',     'id': '9' },
	{ 'name': 'Newsdesk',    'id': '10' },
	{ 'name': 'Highlights',  'id': '11' },
	{ 'name': 'Panel Shows', 'id': '13' },
]

# Team ID (or channel number) was discovered from http://bigpondvideo.com/
# and using a web proxy, extract the AMF data when clicking each channel
# to find its 'NavID' 
TEAMS = [
	{ 'name': 'Adelaide',            'id': '14',   'thumb': 'adel.gif' },
	{ 'name': 'Brisbane',            'id': '22',   'thumb': 'bris.gif' },
	{ 'name': 'Carlton',             'id': '30',   'thumb': 'carl.gif' },
	{ 'name': 'Collingwood',         'id': '38',   'thumb': 'coll.gif' },
	{ 'name': 'Essendon',            'id': '46',   'thumb': 'ess.gif'  },
	{ 'name': 'Fremantle',           'id': '54',   'thumb': 'frem.gif' },
	{ 'name': 'Gold Coast',          'id': '2734', 'thumb': 'gcfc.gif' },
	{ 'name': 'Geelong',             'id': '62',   'thumb': 'geel.gif' },
	{ 'name': 'Greater West Sydney', 'id': '3798', 'thumb': 'gws.gif'  },
	{ 'name': 'Hawthorn',            'id': '70',   'thumb': 'haw.gif'  },
	{ 'name': 'Melbourne',           'id': '86',   'thumb': 'melb.gif' },
	{ 'name': 'North Melbourne',     'id': '78',   'thumb': 'nmfc.gif' },
	{ 'name': 'Port Adelaide',       'id': '94',   'thumb': 'port.gif' },
	{ 'name': 'Richmond',            'id': '102',  'thumb': 'rich.gif' },
	{ 'name': 'St. Kilda',           'id': '110',  'thumb': 'stk.gif'  },
	{ 'name': 'Sydney',              'id': '118',  'thumb': 'syd.gif'  },
	{ 'name': 'West Coast',          'id': '126',  'thumb': 'wce.gif'  },
	{ 'name': 'Western Bulldogs',    'id': '134',  'thumb': 'wb.gif'   },
]

