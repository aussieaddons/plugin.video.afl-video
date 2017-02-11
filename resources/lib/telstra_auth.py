#-------------------------------------------------------------------------------
import requests
import collections
import json
import urlparse
import config
import comm
import utils
from exception import AFLVideoException

def get_token(username, password, phone_number):
    """ Obtain a valid token from Telstra, will be used to make requests for 
        Ooyala embed tokens"""
    session = requests.Session()
    session.verify = False
        
    # Send our first login request to AFL API, recieve (unactivated) token
    # and 'msisdn' URL

    session.headers = {'x-media-mis-token': comm.fetch_token()}
    auth_resp = session.post(config.AFL_LOGIN_URL)
    jsondata = json.loads(auth_resp.text)
    token = jsondata.get('uuid')
    spurl = config.SPORTSPASS_URL.format(token)
    session.headers = config.SPORTSPASS_HEADERS
    sp = session.get(spurl)
    msisdn_url = sp.url
    
    # Sign in to telstra.com to recieve cookies, get the SAML auth, and 
    # modify the escape characters so we can send it back later
    session.headers = config.SIGNON_HEADERS
    signon_data = config.SIGNON_DATA
    signon_data.update({'username': username, 'password': password})
    signon = session.post(config.SIGNON_URL, data=signon_data)
    utils.log(signon.url)
    signon_query = dict(urlparse.parse_qsl(urlparse.urlsplit(signon.url)[3]))
    if 'errorcode' in signon_query:
        if signon_query['errorcode'] == '0':
             raise AFLVideoException('Please enter your username in the settings')
        if signon_query['errorcode'] == '1':
             raise AFLVideoException('Please enter your password in the settings')
        if signon_query['errorcode'] == '2':
             raise AFLVideoException('Please enter your username and password in the settings')
        if signon_query['errorcode'] == '3':
             raise AFLVideoException('Please check your username and password in the settings')
    start_index = signon.text.find('SAMLResponse')+21
    end_index = signon.text[start_index:].find('>')-1+start_index
    saml_base64 = signon.text[start_index:end_index].replace(
                                                    '&#xa;', '%0D%0A').replace(
                                                    '&#x3d;', '%3D').replace(
                                                    '&#x2b;', '%2B')
    
    # Send the SAML login data and retrieve the auth token from the response
    session.headers = config.SAML_LOGIN_HEADERS
    session.cookies.set('saml_request_path', msisdn_url)
    saml_data = 'SAMLResponse={0}'.format(saml_base64)
    saml_login = session.post(config.SAML_LOGIN_URL, data=saml_data)
    confirm_url = saml_login.url
    start_index = saml_login.text.find('apiToken')+12
    end_index = saml_login.text[start_index:].find('"')+start_index
    auth_token = saml_login.text[start_index:end_index]

    # 'Order' the subscription package to activate our token/login
    offer_id = dict(urlparse.parse_qsl(urlparse.urlsplit(msisdn_url)[3]))['offerId']
    media_order_headers = config.MEDIA_ORDER_HEADERS
    media_order_headers.update({'Authorization': 'Bearer {0}'.format(auth_token), 
                                'Referer': confirm_url})
    session.headers = media_order_headers
    media_order = session.post(config.MEDIA_ORDER_URL, 
            data=config.MEDIA_ORDER_JSON.format(phone_number, offer_id, token))
    if media_order.status_code == 400:
        raise AFLVideoException('Invalid phone number in settings.')
    return token