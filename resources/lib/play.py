
import classes
import drmhelper
import ooyalahelper
import sys
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
            if v.type == 'B':
                stream_url = comm.get_bc_url(v)
            else:
                stream_url = v.get_url()
            stream_data = {'stream_url': str(stream_url)}

        listitem = xbmcgui.ListItem(label=v.get_title(),
                                    iconImage=v.get_thumbnail(),
                                    thumbnailImage=v.get_thumbnail(),
                                    path=stream_data.get('stream_url'))

        inputstream = drmhelper.check_inputstream(drm=v.live)
        if not inputstream:
            utils.dialog_message(
                'Failed to play stream. Please visit our website at '
                'http://aussieaddons.com/addons/afl/ for more '
                'information.')
            return

        widevine_url = stream_data.get('widevine_url')

        if inputstream and (not v.live or not widevine_url):
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
                                 widevine_url +
                                 '|Content-Type=application%2F'
                                 'x-www-form-urlencoded|A{SSM}|')
        listitem.addStreamInfo('video', v.get_kodi_stream_info())
        listitem.setInfo('video', v.get_kodi_list_item())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
