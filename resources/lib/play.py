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

import classes
import drmhelper
import ooyalahelper
import sys
import xbmc
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils


def play(url):
    try:
        params = utils.get_url(url)
        v = classes.Video()
        v.parse_xbmc_url(url)
        if params.get('isdummy'):
            xbmcgui.Dialog().ok(
                    'Dummy item',
                    'This item is not playable, it is used only to display '
                    'the upcoming schedule. Please check back once the match '
                    'has started. Playable matches will have "LIVE NOW" in '
                    'green next to the title.')
        if 'ooyalaid' in params:
            login_token = None
            if params.get('subscription_required') == 'True':
                login_token = ooyalahelper.get_user_token()

            stream_data = ooyalahelper.get_m3u8_playlist(params['ooyalaid'],
                                                         v.live, login_token)
        else:
            stream_data = {'stream_url': v.get_url()}

        listitem = xbmcgui.ListItem(label=v.get_title(),
                                    iconImage=v.get_thumbnail(),
                                    thumbnailImage=v.get_thumbnail(),
                                    path=stream_data.get('stream_url'))

        if v.live:
            inputstream = drmhelper.check_inputstream()
        else:
            try:
                fullver = xbmc.getInfoLabel(
                    "System.BuildVersion").split(' ')[0]
                ver = fullver[:fullver.find('-')]
                if float(ver) < 17.0:
                    inputstream = False
                else:
                    inputstream = drmhelper.check_inputstream(drm=False)
            except:
                inputstream = False

        if v.live and not inputstream:
            utils.dialog_message(
                'Kodi 18+ is now required to view live streams.')
            return

        if inputstream and not v.live:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            listitem.setProperty('inputstream.adaptive.license_key',
                                 stream_data.get('stream_url'))
        elif v.live:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            listitem.setProperty('inputstream.adaptive.license_type',
                                 'com.widevine.alpha')
            listitem.setProperty('inputstream.adaptive.license_key',
                                 stream_data.get('widevine_url') +
                                 '|Content-Type=application%2F'
                                 'x-www-form-urlencoded|A{SSM}|')
        listitem.addStreamInfo('video', v.get_kodi_stream_info())
        listitem.setInfo('video', v.get_kodi_list_item())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
