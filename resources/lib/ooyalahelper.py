# Ooyalahelper module copyright 2016 Glenn Guy
#
# Ooyalahelper module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ooyalahelper module is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ooyalahelper module. If not, see <http://www.gnu.org/licenses/>.


# This module contains functions for interacting with the Ooyala API

import urllib
import urllib2
import cookielib

import StringIO
import time
import os

from urlparse import parse_qsl
import xml.etree.ElementTree as ET
import json
import base64

import config
import xbmcaddon
import xbmc

cj = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(handler)
addon = xbmcaddon.Addon()

# NRL specific ooyala functions

def fetch_nrl_xml(url, data):
    """ send http POST and return the xml response as string
        remove first 3 characters as these are junk??"""
    req = urllib2.Request(url, data, config.HEADERS)
    xbmc.log("Fetching URL: {0}".format(url))
    res = urllib2.urlopen(req)
    return res.read()[3:]

def get_nrl_user_token(username, password):
    """send user login info and retrieve user id for session"""
    loginXml = fetch_nrl_xml(config.LOGIN_URL, 
                         config.LOGIN_DATA.format(username, password))
    tree = ET.fromstring(loginXml)
    if not tree.find('ErrorCode') == None:
        if tree.find('ErrorCode').text == '1':
            return 'invalid'
        elif tree.find('ErrorCode').text == 'MIS_EMPTY':
            return 'nosub'
    return tree.find('UserToken').text

def create_nrl_userid_xml(userId):
    """ create a small xml file to send with http POST 
        when starting a new video request"""
    root = ET.Element('Subscription')
    ut = ET.SubElement(root, 'UserToken')
    ut.text = userId
    fakefile = StringIO.StringIO()
    tree = ET.ElementTree(root)
    tree.write(fakefile, encoding='UTF-8')
    output = fakefile.getvalue()
    return output

def fetch_nrl_smil(videoId):
    """ contact ooyala server and retrieve smil data to be decoded"""
    url = config.SMIL_URL.format(videoId)
    xbmc.log("Fetching URL: {0}".format(url))
    res = urllib2.urlopen(url)
    return res.read()

def get_nrl_hds_url(encryptedSmil):
    """ decrypt smil data and return HDS url from the xml data"""
    from ooyala import ooyalaCrypto
    decrypt = ooyalaCrypto.ooyalaCrypto()
    smilXml = decrypt.ooyalaDecrypt(encryptedSmil)
    tree = ET.fromstring(smilXml)
    return tree.find('content').find('video').find('httpDynamicStreamUrl').text


def get_nrl_embed_token(userToken, videoId):
    """send our user token to get our embed token, including api key"""
    xml = fetch_nrl_xml(config.EMBED_TOKEN_URL.format(videoId), 
                    create_nrl_userid_xml(userToken))
    tree = ET.fromstring(xml)
    return tree.find('Token').text

# AFL ooyala functions

def fetch_afl_json(url, data):
    """ send http POST and return the json response data"""
    data = urllib.urlencode(data)
    req = urllib2.Request(url, data, config.HEADERS)
    res = urllib2.urlopen(req)
    xbmc.log("Fetching URL: {0}".format(url))
    return res.read()

def get_afl_user_token():
    """send user login info and retrieve user id for session"""
    loginData = {'userIdentifierType': 'EMAIL'}
    loginData['authToken'] = addon.getSetting('password')
    loginData['userIdentifier'] = addon.getSetting('username')
    
    loginJson = fetch_afl_json(config.LOGIN_URL, loginData)
    data = json.loads(loginJson)
    if data['responseCode'] == 1:
        return 'invalid'
    sessionId = data['data'].get('artifactValue')
    
    import comm
    apiToken = comm.fetch_token()
    opener.addheaders = [('x-media-mis-token', apiToken)]
    res = opener.open(config.SESSION_URL.format(urllib.quote(sessionId)))
    data = json.loads(res.read())
    if len(data['subscriptions']) == 0:
        return 'nosub'
    return data['subscriptions'][0].get('uuid')
    
def get_afl_embed_token(userToken, videoId):
    """send our user token to get our embed token, including api key"""
    res = opener.open(config.EMBED_TOKEN_URL.format(userToken, videoId))
    data = json.loads(res.read())
    return data.get('token')

#common ooyala functions
 
def get_secure_token(secureUrl, videoId):
    """send our embed token back with a few other url encoded parameters"""
    res = opener.open(secureUrl,None)
    data = res.read()
    parsed_json = json.loads(data)
    iosToken =  parsed_json['authorization_data'][videoId]['streams'][0]['url']['data']
    return base64.b64decode(iosToken)

def get_m3u8_streams(secureTokenUrl):
    """ fetch our m3u8 file which contains streams of various qualities"""
    res = opener.open(secureTokenUrl, None)
    data = res.readlines()
    return data

def parse_m3u8_streams(data, live, secureTokenUrl):
    """ Parse the retrieved m3u8 stream list into a list of dictionaries
        then return the url for the highest quality stream. Different 
        handling is required of live m3u8 files as they seem to only contain
        the destination filename and not the domain/path."""
    if live == 'true':
        qual = xbmcaddon.Addon().getSetting('LIVEQUALITY')
    else:
        qual = xbmcaddon.Addon().getSetting('HLSQUALITY')

    count = 1
    m3uList = []
    prependLive = secureTokenUrl[:secureTokenUrl.find('index-root')]
    
    while count < len(data):
        line = data[count]
        line = line.strip('#EXT-X-STREAM-INF:')
        line = line.strip('PROGRAM-ID=1,')
        line = line[:line.find('CODECS')]
        
        if line.endswith(','):
            line = line[:-1]
        
        line = line.strip()
        line = line.split(',')
        linelist = [i.split('=') for i in line]
        
        if live == 'false':
            linelist.append(['URL',data[count+1]])
        else:
            linelist.append(['URL',prependLive+data[count+1]])
        
        m3uList.append(dict((i[0], i[1]) for i in linelist))
        count += 2
    
    sorted_m3uList = sorted(m3uList, key=lambda k: int(k['BANDWIDTH']))
    stream = sorted_m3uList[int(qual)]['URL'][:-2]   
    return stream

def cookies_to_string(cookiejar):
    result = "|Cookie=Cookie: "
    for cookie in cookiejar:
        result += cookie.name
        result += '='
        result += cookie.value
        result += ';'
    result = result[:-1]
    return result 
    
def get_m3u8_playlist(videoId, live, loginToken, mode):
    """ Main function to call other functions that will return us our m3u8 HLS
        playlist as a string, which we can then write to a file for Kodi
        to use"""
    if mode == 'AFL':
        embedToken = get_afl_embed_token(loginToken, videoId)
        
    elif mode == 'NRL':
        embedToken = get_nrl_embed_token(loginToken, videoId)
        
    authorizeUrl = config.AUTH_URL.format(config.PCODE, videoId, embedToken)
    secureTokenUrl = get_secure_token(authorizeUrl, videoId)
    m3u8Data = get_m3u8_streams(secureTokenUrl)
    m3u8PlaylistUrl = parse_m3u8_streams(m3u8Data, live, secureTokenUrl)
    pipe = cookies_to_string(cj)
    return m3u8PlaylistUrl+pipe
















