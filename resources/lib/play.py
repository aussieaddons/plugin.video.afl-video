import sys
from distutils.version import LooseVersion

from aussieaddonscommon import utils

import drmhelper

from resources.lib import classes
from resources.lib import comm
from resources.lib import stream_auth

import xbmcgui

import xbmcplugin


def play(url):
    try:
        params = utils.get_url(url)
        v = classes.Video()
        v.parse_kodi_url(url)
        live = v.live == 'True'
        if params.get('isdummy'):
            xbmcgui.Dialog().ok(
                    'Dummy item',
                    'This item is not playable, it is used only to display '
                    'the upcoming schedule. Please check back once the match '
                    'has started. Playable matches will have "LIVE NOW" in '
                    'green next to the title.')
            return
        if live:
            media_auth_token = None
            if params.get('subscription_required') == 'True':
                media_auth_token = stream_auth.get_media_auth_token(
                    stream_auth.get_user_token(), v.video_id)
            stream_url = comm.get_stream_url(v, media_auth_token)
            stream_data = {'stream_url': str(stream_url)}
        else:
            stream_url = comm.get_bc_url(v)
            stream_data = {'stream_url': str(stream_url)}

        thumb = v.get_thumbnail()
        listitem = xbmcgui.ListItem(label=v.get_title(),
                                    path=stream_data.get('stream_url'))
        listitem.setArt({'icon': thumb, 'thumb': thumb})

        if not live:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            listitem.setProperty('inputstream.adaptive.license_key',
                                 stream_data.get('stream_url'))

        else:
            drm_helper = drmhelper.helper.DRMHelper()
            addon = drm_helper.get_addon()
            if addon:
                ia_ver = addon.getAddonInfo('version')
                kodi_ver = utils.get_kodi_major_version()
                ia_capable = False
                if kodi_ver == 18:
                    if LooseVersion(ia_ver) >= LooseVersion('2.4.3'):
                        ia_capable = True
                elif kodi_ver == 19:
                    if LooseVersion(ia_ver) >= LooseVersion('2.5.4'):
                        ia_capable = True
                if ia_capable:
                    listitem.setProperty('inputstreamaddon',
                                         'inputstream.adaptive')
                    listitem.setProperty('inputstream.adaptive.manifest_type',
                                         'hls')
                    listitem.setProperty('inputstream.adaptive.license_key',
                                         stream_data.get('stream_url'))

        listitem.addStreamInfo('video', v.get_kodi_stream_info())
        listitem.setInfo('video', v.get_kodi_list_item())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
