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
    session = custom_session.Session(force_tlsv1=False)

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
    session.headers = config.SSO_HEADERS
    session.headers.update({'Cookie': 'BPSESSION={0}'.format(bp_session)})
    sso_token_resp = session.get(signon.headers.get('Location'))

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

    ents = json.loads(
        session.get(config.ENTITLEMENTS_URL).text).get('entitlements')
    
    for service in ents:
        utils.log(service.get('startDate'))
        utils.log(service.get('endDate'))
        utils.log(service.get('status'))
        utils.log('{0}XXXXX'.format(service.get('serviceId')[:6]))
    
    service_ids = [x['serviceId'] for x in ents if x['status'] == 'Active']
        
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
            raise TelstraAuthException(e)
    try:
        offer_data = json.loads(offers.text)
        offers_list = offer_data['data']['offers']
        ph_no = None
        for offer in offers_list:
            if offer.get('name') != 'AFL Live Pass':
                continue
            from copy import deepcopy
            offer_copy = deepcopy(offer)
            if offer_copy.get('productOfferingAttributes')[2].get('name') == 'ServiceId':
                offer_copy.get('productOfferingAttributes')[2]['value'] = '{0}XXXXX'.format(offer_copy.get('productOfferingAttributes')[2]['value'][:6])
                utils.log('Product offer is: {0}'.format(offer_copy))
            
            utils.log('Offer reuptake: {0}'.format(offer.get('reuptakeAllowed')))
            data = offer.get('productOfferingAttributes')
            serv_id = [x['value'] for x in data if x['name'] == 'ServiceId'][0]
            if serv_id in service_ids:
                ph_no = serv_id
                break
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


def get_mobile_token():
    session = custom_session.Session(force_tlsv1=False)
    prog_dialog = xbmcgui.DialogProgress()
    prog_dialog.create('Logging in with mobile service')
    prog_dialog.update(1, 'Obtaining oauth token')
    comm.update_token(session)
    auth_resp = session.post(config.AFL_LOGIN_URL)
    jsondata = json.loads(auth_resp.text)
    userid = jsondata.get('uuid')
    if not userid:
        raise TelstraAuthException('Unable to get token from AFL API')

    prog_dialog.update(20, 'Obtaining mobile token')
    mobile_userid_cookies = session.get(
        config.MOBILE_ID_URL).cookies.get_dict()
    mobile_userid = mobile_userid_cookies.get('GUID_S')
    if not mobile_userid or mobile_userid_cookies.get('nouid'):
        raise TelstraAuthException('Not connected to Telstra Mobile network. '
                                   'Please disable WiFi and enable mobile '
                                   'data if on a Telstra mobile device, or '
                                   "connect this device's WiFi to a device "
                                   'that is on the Telstra Mobile network '
                                   'and try again.')
    data = config.MOBILE_TOKEN_PARAMS
    data.update({'x-user-id': mobile_userid})
    mobile_token_resp = session.post(config.OAUTH_URL, data=data)
    bearer_token = json.loads(mobile_token_resp.text).get('access_token')

    # First check if there are any eligible services attached to the account
    prog_dialog.update(40, 'Determining eligible services')
    session.headers = config.OAUTH_HEADERS
    session.headers.update(
        {'Authorization': 'Bearer {0}'.format(bearer_token)})
    try:
        offers = session.get(config.OLD_OFFERS_URL)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            message = json.loads(e.response.text).get('userMessage')
            message += (' Please visit {0} '.format(config.HUB_URL) +
                        'for further instructions to link your mobile '
                        'service to the supplied Telstra ID')
            raise TelstraAuthException(message)
        else:
            raise TelstraAuthException(e)
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
    prog_dialog.update(60, 'Activating live pass on service')
    order_data = config.MOBILE_ORDER_JSON
    order_data.update({'serviceId': ph_no, 'pai': userid})
    order = session.post(config.OLD_MEDIA_ORDER_URL, json=order_data)

    # check to make sure order has been placed correctly
    prog_dialog.update(80, 'Confirming activation')
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
    return userid
