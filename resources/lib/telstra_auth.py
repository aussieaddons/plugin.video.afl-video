import json
import urlparse
import config
import comm
import re
import utils
import urllib
import ssl

from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.poolmanager import PoolManager


# Ignore InsecureRequestWarning warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class TelstraAuthException(Exception):
    """ A Not Fatal Exception is used for certain conditions where we do not
        want to give users an option to send an error report
    """
    pass


class TLSv1Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)


def get_token(username, password):
    """ Obtain a valid token from Telstra, will be used to make requests for
        Ooyala embed tokens"""
    session = requests.Session()
    session.mount('https://', TLSv1Adapter())
    session.verify = False

    # Send our first login request to AFL API, recieve (unactivated) token
    # and 'msisdn' URL
    session.headers = {'x-media-mis-token': comm.fetch_token()}
    auth_resp = session.post(config.AFL_LOGIN_URL)
    jsondata = json.loads(auth_resp.text)
    token = jsondata.get('uuid')
    if not token:
        raise TelstraAuthException('Unable to get token from AFL API')

    spurl = config.SPORTSPASS_URL.format(token)
    session.headers = config.SPORTSPASS_HEADERS
    sp = session.get(spurl)
    msisdn_url = sp.url

    # Sign in to telstra.com to recieve cookies, get the SAML auth, and
    # modify the escape characters so we can send it back later
    utils.log('Signing in to: {0}'.format(config.SIGNON_URL))
    session.headers = config.SIGNON_HEADERS
    signon_data = config.SIGNON_DATA
    signon_data.update({'username': username, 'password': password})
    signon = session.post(config.SIGNON_URL, data=signon_data)

    signon_pieces = urlparse.urlsplit(signon.url)
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
            raise TelstraAuthException('Please check your username and '
                                       'password in the settings')

    soup = BeautifulSoup(signon.text, 'html.parser')
    saml_response = soup.find(attrs={'name': 'SAMLResponse'}).get('value')
    saml_base64 = urllib.quote(saml_response)

    # Send the SAML login data and retrieve the auth token from the response
    session.headers = config.SAML_LOGIN_HEADERS
    session.cookies.set('saml_request_path', msisdn_url)
    saml_data = 'SAMLResponse=' + saml_base64
    utils.log('Fetching stream auth token: {0}'.format(config.SAML_LOGIN_URL))
    saml_login = session.post(config.SAML_LOGIN_URL, data=saml_data)

    confirm_url = saml_login.url
    auth_token_match = re.search('apiToken = "(\w+)"', saml_login.text)
    if auth_token_match:
        auth_token = auth_token_match.group(1)
        utils.log('Found auth token: {0}'.format(auth_token))
    else:
        raise TelstraAuthException('Could not obtain authorisation token')

    # 'Order' the subscription package to activate our token/login
    msisdn_pieces = urlparse.urlsplit(msisdn_url)
    msisdn_query = urlparse.parse_qsl(msisdn_pieces.query)
    offer_id = dict(msisdn_query).get('offerId')

    if not offer_id:
        raise TelstraAuthException('Could not find streaming offer ID')

    media_order_hdrs = config.MEDIA_ORDER_HEADERS
    media_order_hdrs.update({'Authorization': 'Bearer {0}'.format(auth_token),
                             'Referer': confirm_url})
    session.headers = media_order_hdrs
    
    # First check if there are any eligible services attached to the account
    offers = session.get('https://api.telstra.com/v1/media-products/catalogues/media/offers?category=afl')
    try:
        offers.raise_for_status()
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
        for offer in offers_list:
            if offer.get('name') != 'AFL Live Pass':
                continue
            data = offer.get('productOfferingAttributes')
            ph_no = [x['value'] for x in data if x['name'] == 'ServiceId'][0]
    except:
        raise TelstraAuthException('Unable to determine eligible services')
    
    media_order_data = config.MEDIA_ORDER_JSON.format(ph_no,
                                                      offer_id,
                                                      token)
    media_order = session.post(config.MEDIA_ORDER_URL, media_order_data)
    return token