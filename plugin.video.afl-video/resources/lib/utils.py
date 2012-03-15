import re
import htmlentitydefs
import cgi

import urllib

import config

pattern = re.compile("&(\w+?);")

def descape_entity(m, defs=htmlentitydefs.entitydefs):
	# callback: translate one entity to its ISO Latin value
	try:
		return defs[m.group(1)]
	except KeyError:
		return m.group(0) # use as is

def descape(string):
	# Fix the hack back from parsing with BeautifulSoup
	string = string.replace('&#38;', '&amp;')

	return pattern.sub(descape_entity, string)

def get_url(s):
	dict = {}
	pairs = s.lstrip("?").split("&")
	for pair in pairs:
		if len(pair) < 3: continue
		kv = pair.split("=",1)
		k = kv[0]
		v = urllib.unquote_plus(kv[1])
		dict[k] = v
	return dict

def make_url(d):
	pairs = []
	for k,v in d.iteritems():
		k = urllib.quote_plus(k)
		v = urllib.quote_plus(str(v))
		pairs.append("%s=%s" % (k,v))
	return "&".join(pairs)

def log(s):
	print "[%s v%s] %s" % (config.NAME, config.VERSION, s)
