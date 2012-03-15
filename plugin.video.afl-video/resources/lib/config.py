import os

NAME = 'AFL Video'
VERSION = '0.1'

# Video quality
QUAL_LOW = 0
QUAL_MED = 1
QUAL_HIGH = 2

CHANNELS = [
	{ 'name': 'Teams',       'id': 'teams' },
	{ 'name': 'Matches',     'id': '9' },
	{ 'name': 'Newsdesk',    'id': '10' },
	{ 'name': 'Highlights',  'id': '11' },
	{ 'name': 'Panel Shows', 'id': '13'},
]

# Team ID (or channel number) was discovered from http://bigpondvideo.com/
# and using a web proxy, extract the AMF data when clicking each channel
# to find its 'NavID' 
TEAMS = [
	{ 'name': 'Adelaide',            'id': '14' },
	{ 'name': 'Brisbane',            'id': '22' },
	{ 'name': 'Carlton',             'id': '30' },
	{ 'name': 'Collingwood',         'id': '38' },
	{ 'name': 'Essendon',            'id': '46' },
	{ 'name': 'Fremantle',           'id': '54' },
	{ 'name': 'Gold Coast',          'id': '2734' },
	{ 'name': 'Geelong',             'id': '62' },
	{ 'name': 'Greater West Sydney', 'id': '3798' },
	{ 'name': 'Hawthorn',            'id': '70' },
	{ 'name': 'Melbourne',           'id': '86' },
	{ 'name': 'North Melbourne',     'id': '78' },
	{ 'name': 'Port Adelaide',       'id': '94' },
	{ 'name': 'Richmond',            'id': '102' },
	{ 'name': 'St. Kilda',           'id': '110' },
	{ 'name': 'Sydney',              'id': '118' },
	{ 'name': 'West Coast',          'id': '126' },
	{ 'name': 'Western Bulldogs',    'id': '134' },
]

