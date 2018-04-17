import binascii
import comm
import config
import json
import os
import re
import requests
import urlparse
import xbmcgui

from aussieaddonscommon.exceptions import AussieAddonsException
from aussieaddonscommon import session as custom_session
from aussieaddonscommon import utils


class TelstraAuthException(AussieAddonsException):
    """Telstra Auth exception

    This exception can be thrown with the reportable arg set which can
    determine whether or not it is allowed to be sent as an automatic
    error report
    """
    pass


def get_token(username, password):
    """Fetch token for Telstra auth

    Obtain a valid token from Telstra, will be used to make requests for
    Ooyala embed tokens
    """
    session = custom_session.Session(force_tlsv1=True)

    prog_dialog = xbmcgui.DialogProgress()
    prog_dialog.create('Logging in with Telstra ID')
    prog_dialog.update(1, 'Obtaining user token')

    # Send our first login request to AFL API, recieve (unactivated) token
    # and 'msisdn' URL
    comm.update_token(session)
    auth_resp = session.post(config.AFL_LOGIN_URL)
    jsondata = json.loads(auth_resp.text)
    token = jsondata.get('uuid')
    if not token:
        raise TelstraAuthException('Unable to get token from AFL API')

    prog_dialog.update(20, 'Getting SSO Client ID')
    # GET to our spc url and receive SSO client ID
    spc_url = config.SPORTSPASS_URL.format(token)
    session.headers = config.SPC_HEADERS
    spc_resp = session.get(spc_url)
    sso_token_match = re.search('ssoClientId = "(\w+)"', spc_resp.text)
    try:
        sso_token = sso_token_match.group(1)
    except AttributeError as e:
        utils.log('SPC login response: {0}'.format(spc_resp.text))
        raise e

    # Sign in to telstra.com with our SSO client id to get the url
    # for retrieving the bearer token for media orders
    prog_dialog.update(40, 'Signing on to telstra.com')
    sso_params = config.SSO_PARAMS
    sso_params.update({'client_id': sso_token,
                       'state': binascii.b2a_hex(os.urandom(16)),
                       'nonce': binascii.b2a_hex(os.urandom(16))})

    sso_auth_resp = session.get(config.SSO_URL, params=sso_params)
    sso_url = dict(urlparse.parse_qsl(
                   urlparse.urlsplit(sso_auth_resp.url)[3])).get('goto')

    # login to telstra.com.au and get our BPSESSION cookie
    session.headers.update(config.SIGNON_HEADERS)
    signon_data = config.SIGNON_DATA
    signon_data = {'username': username, 'password': password, 'goto': sso_url}
    signon = session.post(config.SIGNON_URL,
                          data=signon_data,
                          allow_redirects=False)
    bp_session = session.cookies.get_dict().get('BPSESSION')

    # check signon is valid (correct username/password)

    signon_pieces = urlparse.urlsplit(signon.headers.get('Location'))
    signon_query = dict(urlparse.parse_qsl(signon_pieces.query))

    utils.log('Sign-on result: %s' % signon_query)

    if 'errorcode' in signon_query:
        if signon_query['errorcode'] == '0':
            raise TelstraAuthException('Please enter your username '
                                       'in the settings')
        if signon_query['errorcode'] == '1':
            raise TelstraAuthException('Please enter your password '
                                       'in the settings')
        if signon_query['errorcode'] == '2':
            raise TelstraAuthException('Please enter your username and '
                                       'password in the settings')
        if signon_query['errorcode'] == '3':
            raise TelstraAuthException('Invalid Telstra ID username/password. '
                                       'Please check your username and '
                                       'password in the settings')

    # Use BPSESSION cookie to ask for bearer token
    sso_headers = config.SSO_HEADERS
    sso_headers.update({'Cookie': 'BPSESSION={0}'.format(bp_session)})
    session.headers = sso_headers
    sso_token_resp = session.get(sso_url)
    bearer_token = dict(urlparse.parse_qsl(
                    urlparse.urlsplit(sso_token_resp.url)[4]))['access_token']

    # First check if there are any eligible services attached to the account
    prog_dialog.update(60, 'Determining eligible services')
    offer_id = dict(urlparse.parse_qsl(
                    urlparse.urlsplit(spc_url)[3]))['offerId']
    media_order_headers = config.MEDIA_ORDER_HEADERS
    media_order_headers.update(
        {'Authorization': 'Bearer {0}'.format(bearer_token)})
    session.headers = media_order_headers
    try:
        offers = session.get(config.OFFERS_URL)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            message = json.loads(e.response.text).get('userMessage')
            message += (' Please visit {0} '.format(config.HUB_URL) +
                        'for further instructions to link your mobile '
                        'service to the supplied Telstra ID')
            raise TelstraAuthException(message)
        else:
            raise TelstraAuthException(e.response.status_code)
    try:
        offer_data = json.loads(offers.text)
        offers_list = offer_data['data']['offers']
        ph_no = None
        for offer in offers_list:
            if offer.get('name') != 'AFL Live Pass':
                continue
            data = offer.get('productOfferingAttributes')
            ph_no = [x['value'] for x in data if x['name'] == 'ServiceId'][0]
        if not ph_no:
            raise TelstraAuthException(
                'Unable to determine if you have any eligible services. '
                'Please ensure there is an eligible service linked to '
                'your Telstra ID to redeem the free offer. Please visit '
                '{0} for further instructions'.format(config.HUB_URL))
    except Exception as e:
        raise e

    # 'Order' the subscription package to activate the service
    prog_dialog.update(80, 'Activating live pass on service')
    order_data = config.MEDIA_ORDER_JSON.format(ph_no, offer_id, token)
    order = session.post(config.MEDIA_ORDER_URL, data=order_data)

    # check to make sure order has been placed correctly
    if order.status_code == 201:
        try:
            order_json = json.loads(order.text)
            status = order_json['data'].get('status') == 'COMPLETE'
            if status:
                utils.log('Order status complete')
        except:
            utils.log('Unable to check status of order, continuing anyway')
    session.close()
    prog_dialog.update(100, 'Finished!')
    prog_dialog.close()
    return token
