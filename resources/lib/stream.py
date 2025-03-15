# -*- coding: utf-8 -*-
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon

from datetime import datetime
import time

from resources.lib.session import Session
from resources.lib.api import API
from resources.lib.channels import Channels
from resources.lib.epg import get_channel_epg
from resources.lib.utils import PY2

if len(sys.argv) > 1:
    _handle = int(sys.argv[1])

def play_catchup(id, start_ts, end_ts):
    start_ts = int(start_ts)
    end_ts = int(end_ts)    
    epg = get_channel_epg(channel_id = id, from_ts = start_ts, to_ts = end_ts + 60*60*12)
    if start_ts in epg:
        if epg[start_ts]['endts'] > int(time.mktime(datetime.now().timetuple()))-10:
            play_live(id, 'start')
        else:
            play_archive(id = epg[start_ts]['id'])
    else:
        play_live(id, 'live')

def play_live(id, mode):
    addon = xbmcaddon.Addon()
    session = Session()
    api = API()
    channels = Channels()
    channels_list = channels.get_channels_list('id')
    channel = channels_list[id]
    if channel['adult'] == True:
        if str(addon.getSetting('pin')) == '1621' or len(str(addon.getSetting('pin'))) == 0:
            pin = xbmcgui.Dialog().numeric(type = 0, heading = 'Zadejte PIN', bHiddenInput = True)
            if len(str(pin)) != 4:
                xbmcgui.Dialog().notification('Oneplay','Nezadaný-nesprávný PIN', xbmcgui.NOTIFICATION_ERROR, 5000)
                pin = '1621'
        else:
            pin = str(addon.getSetting('pin'))
        post = {"authorization":[{"schema":"PinRequestAuthorization","pin":pin,"type":"parental"}],"payload":{"criteria":{"schema":"ContentCriteria","contentId":"channel." + id},"startMode":"live"},"playbackCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","subtitle":{"formats":["vtt"],"locations":["InstreamTrackLocation","ExternalTrackLocation"]},"liveSpecificCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","multipleAudio":False}}}
    else:
        post = {"payload":{"criteria":{"schema":"ContentCriteria","contentId":"channel." + id},"startMode":mode},"playbackCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","subtitle":{"formats":["vtt"],"locations":["InstreamTrackLocation","ExternalTrackLocation"]},"liveSpecificCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","multipleAudio":False}}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/content.play', data = post, session = session)
    if 'err' in data or 'media' not in data:
        xbmcgui.Dialog().notification('Oneplay','Problém při přehrání', xbmcgui.NOTIFICATION_ERROR, 5000)
    if 'liveControl' in ['playerControl'] and 'mosaic' in data['playerControl']['liveControl']:
        md_titles = []
        md_ids = []
        for item in data['playerControl']['liveControl']['mosaic']['items']:
            md_titles.append(item['title'])
            md_ids.append(item['play']['params']['payload']['criteria']['contentId'])            
        response = xbmcgui.Dialog().select(heading = 'Multidimenze - výběr streamu', list = md_titles, preselect = 0)
        if response < 0:
            return
        id = md_ids[response]
        post = {"payload":{"criteria":{"schema":"MDPlaybackCriteria","contentId":id,"position":0},"startMode":mode},"playbackCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","subtitle":{"formats":["vtt"],"locations":["InstreamTrackLocation","ExternalTrackLocation"]},"liveSpecificCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","multipleAudio":False}}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/content.play', data = post, session = session)
        if 'err' in data or 'media' not in data:
            xbmcgui.Dialog().notification('Oneplay','Problém při přehrání', xbmcgui.NOTIFICATION_ERROR, 5000)
    play_stream(data)

def play_archive(id):
    session = Session()
    api = API()
    post = {"payload":{"criteria":{"schema":"ContentCriteria","contentId":id}},"playbackCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","subtitle":{"formats":["vtt"],"locations":["InstreamTrackLocation","ExternalTrackLocation"]},"liveSpecificCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","multipleAudio":False}}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/content.play', data = post, session = session)
    if 'err' in data or 'media' not in data:
        xbmcgui.Dialog().notification('Oneplay','Problém při přehrání', xbmcgui.NOTIFICATION_ERROR, 5000)
    if 'liveControl' in ['playerControl'] and 'mosaic' in data['playerControl']['liveControl']:
        md_titles = []
        md_ids = []
        for item in data['playerControl']['liveControl']['mosaic']['items']:
            md_titles.append(item['title'])
            md_ids.append(item['play']['params']['payload']['criteria']['contentId'])            
        response = xbmcgui.Dialog().select(heading = 'Multidimenze - výběr streamu', list = md_titles, preselect = 0)
        if response < 0:
            return
        id = md_ids[response]
        post = {"payload":{"criteria":{"schema":"MDPlaybackCriteria","contentId":id,"position":0}},"playbackCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","subtitle":{"formats":["vtt"],"locations":["InstreamTrackLocation","ExternalTrackLocation"]},"liveSpecificCapabilities":{"protocols":["dash","hls"],"drm":["widevine","fairplay"],"altTransfer":"Unicast","multipleAudio":False}}}
        data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/content.play', data = post, session = session)
        if 'err' in data or 'media' not in data:
            xbmcgui.Dialog().notification('Oneplay','Problém při přehrání', xbmcgui.NOTIFICATION_ERROR, 5000)
    play_stream(data)

def play_stream(data):
    url_dash = None
    url_dash_drm = None
    url_hls = None
    if 'media' in data:
        for asset in data['media']['stream']['assets']:
            if asset['protocol'] == 'dash':
                if 'drm' in asset:
                    url_dash_drm = asset['src']
                    drm = {'token' : asset['drm'][0]['drmAuthorization']['value'], 'licenceUrl' : asset['drm'][0]['licenseAcquisitionURL']}
                else:
                    url_dash = asset['src']
            if asset['protocol'] == 'hls':
                if 'clear' in asset['src']:
                    url_hls = asset['src']
        if url_dash is not None:
            list_item = xbmcgui.ListItem(path = url_dash)
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            if PY2:
                list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            list_item.setMimeType('application/dash+xml')
            list_item.setContentLookup(False)       
            xbmcplugin.setResolvedUrl(_handle, True, list_item)
        elif url_dash_drm is not None:
            list_item = xbmcgui.ListItem(path = url_dash_drm)
            list_item.setProperty('inputstream', 'inputstream.adaptive')
            if PY2:
                list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
            list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
            if drm is not None:
                from inputstreamhelper import Helper # type: ignore
                is_helper = Helper('mpd', drm = 'com.widevine.alpha')
                if is_helper.check_inputstream():            
                    list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
                    from urllib.parse import urlencode
                    list_item.setProperty('inputstream.adaptive.license_key', drm['licenceUrl'] + '|' + urlencode({'x-axdrm-message' : drm['token']}) + '|R{SSM}|')                
            list_item.setMimeType('application/dash+xml')
            list_item.setContentLookup(False)       
            xbmcplugin.setResolvedUrl(_handle, True, list_item)
        elif url_hls is not None:
            list_item = xbmcgui.ListItem(path = url_hls)
            list_item.setContentLookup(False)       
            xbmcplugin.setResolvedUrl(_handle, True, list_item)
    else:
        xbmcgui.Dialog().notification('Oneplay','Problém při přehrání', xbmcgui.NOTIFICATION_ERROR, 5000)
