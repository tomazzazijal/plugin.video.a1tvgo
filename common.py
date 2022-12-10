# -*- coding: utf-8 -*-
import sys
PY2 = sys.version_info[0] == 2
import xbmc, xbmcaddon
import uuid
if PY2:
    from urllib import urlencode
    import urllib2
    import urlparse
else:
    import urllib.request
    import urllib.parse
import datetime, time, pytz
import json
from lib.graphqlclient import GraphQLClient

def debug(obj):
    xbmc.log(json.dumps(obj, indent=2), xbmc.LOGDEBUG)

username = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_username')
password = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_password')
user_id = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_user_id')
session_id = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_session_id')
max_bandwidth = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_max_bandwidth')
if xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_adult') == "false":
    adult_setting = False
else:
    adult_setting = True
if PY2:
    args = urlparse.parse_qs(sys.argv[2][1:])
else:
    args = urllib.parse.parse_qs(sys.argv[2][1:])

device_id = args.get('device_id',[''])[0]
if not device_id:
    device_id = xbmcaddon.Addon(id='plugin.video.a1tvgo').getSetting('settings_device_id')
    if not device_id:
        mac = xbmc.getInfoLabel('Network.MacAddress')
        while mac == 'Busy':
            time.sleep(0.5)
            mac = xbmc.getInfoLabel('Network.MacAddress')
        device_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, mac))
        xbmcaddon.Addon(id='plugin.video.a1tvgo').setSetting('settings_device_id', device_id)

class my_gqlc(GraphQLClient):
    def __init__(self, headers):
        self.endpoint = 'https://web.xploretv.si:8443/sdsmiddleware/A1_Slovenia/graphql/4.0'
        self.headers = headers
    def execute(self, query, variables=None):
        debug(self.headers)
        debug(query.partition('\n')[0])
        res = self._send(query, variables, self.headers)
        debug(res)
        return res

def to_datetime(instr):
    return datetime.datetime(*(time.strptime(instr, '%Y-%m-%dT%H:%M:%SZ')[0:6])).replace(tzinfo=pytz.timezone('UTC')).astimezone(pytz.timezone('Europe/Sofia'))

def request(action, params={}, method='POST'):
    endpoint = 'https://web.xploretv.si:8843/ext_dev_facade/auth/'
    data = {}
    data.update(params)
    debug(action)
    debug(data)
    if PY2:
        tmp = ''
        if method == 'GET':
            tmp = None
        req = urllib2.Request(endpoint + action + '?%s' % urlencode(data), data=tmp)
    else:
        req = urllib.request.Request(endpoint + action + '?%s' % urllib.parse.urlencode(data), method=method)
    req.add_header('Content-Type', 'application/json')
    if PY2:
        f = urllib2.urlopen(req)
    else:
        f = urllib.request.urlopen(req)
    responce = f.read()
    json_responce = json.loads(responce)
    debug(json_responce)
    return json_responce
