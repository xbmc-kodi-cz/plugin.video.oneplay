# -*- coding: utf-8 -*-
import xbmc
import time

from resources.lib.session import Session
from resources.lib.api import API
from resources.lib.utils import get_kodi_version

from datetime import datetime

def get_live_epg():
    session = Session()
    api = API()
    epg = {}
    today_date = datetime.today() 
    from_ts = int(time.mktime(datetime(today_date.year, today_date.month, today_date.day).timetuple()))
    to_ts = from_ts + 60*60*24 - 1
    post = {"payload":{"criteria":{"channelSetId":"channel_list.1","viewport":{"channelRange":{"from":0,"to":200},"timeRange":{"from":datetime.fromtimestamp(from_ts).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z',"to":datetime.fromtimestamp(to_ts).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'},"schema":"EpgViewportAbsolute"}},"requestedOutput":{"channelList":"none","datePicker":False,"channelSets":False}}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/epg.display', data = post, session = session)
    if 'err' not in data:
        for channel in data['schedule']:
            for item in channel['items']:
                startts = int(datetime.fromisoformat(item['startAt']).timestamp())
                endts = int(datetime.fromisoformat(item['endAt']).timestamp())
                currentts = datetime.now().timestamp()
                if startts < currentts and endts > currentts:
                    epg_item = {'id' : item['id'], 'title' : item['title'], 'channel_id' : id, 'description' : item['description'], 'startts' : startts, 'endts' : endts, 'cover' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320'), 'poster' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320')}
                    epg.update({channel['channelId'] : epg_item})
    return epg

def get_channel_epg(channel_id, from_ts, to_ts):
    session = Session()
    api = API()
    epg = {}
    post = {"payload":{"criteria":{"channelSetId":"channel_list.1","viewport":{"channelRange":{"from":0,"to":200},"timeRange":{"from":datetime.fromtimestamp(from_ts-3600).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z',"to":datetime.fromtimestamp(to_ts-3600).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'},"schema":"EpgViewportAbsolute"}},"requestedOutput":{"channelList":"none","datePicker":False,"channelSets":False}}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/epg.display', data = post, session = session)
    if 'err' not in data:
        for channel in data['schedule']:
            if channel['channelId'] == channel_id:
                for item in channel['items']:
                    startts = int(datetime.fromisoformat(item['startAt']).timestamp())
                    endts = int(datetime.fromisoformat(item['endAt']).timestamp())
                    if item['actions'][0]['params']['contentType'] in ['show','movie']:
                        id = item['actions'][0]['params']['payload']['deeplink']['epgItem']
                    else:
                        id = item['actions'][0]['params']['payload']['contentId']
                    epg_item = {'id' : id, 'title' : item['title'], 'channel_id' : channel_id, 'description' : item['description'], 'startts' : startts, 'endts' : endts, 'cover' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320'), 'poster' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320')}
                    epg.update({startts : epg_item})
    return epg

def get_day_epg(from_ts, to_ts):
    session = Session()
    api = API()
    epg = {}
    post = {"payload":{"criteria":{"channelSetId":"channel_list.1","viewport":{"channelRange":{"from":0,"to":200},"timeRange":{"from":datetime.fromtimestamp(from_ts).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z',"to":datetime.fromtimestamp(to_ts).strftime('%Y-%m-%dT%H:%M:%S') + '.000Z'},"schema":"EpgViewportAbsolute"}},"requestedOutput":{"channelList":"none","datePicker":False,"channelSets":False}}}
    data = api.call_api(url = 'https://http.cms.jyxo.cz/api/v3/epg.display', data = post, session = session)
    if 'err' not in data:
        for channel in data['schedule']:
            for item in channel['items']:
                startts = int(datetime.fromisoformat(item['startAt']).timestamp())
                endts = int(datetime.fromisoformat(item['endAt']).timestamp())
                if 'contentType' in item['actions'][0]['params'] or 'contentId' in item['actions'][0]['params']['payload']:
                    if item['actions'][0]['params']['contentType'] == 'show':
                        id = item['actions'][0]['params']['payload']['deeplink']['epgItem']
                    else:
                        id = item['actions'][0]['params']['payload']['contentId']
                    epg_item = {'id' : id, 'title' : item['title'], 'channel_id' : channel['channelId'], 'description' : item['description'], 'startts' : startts, 'endts' : endts, 'cover' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320'), 'poster' : item['image'].replace('{WIDTH}', '480').replace('{HEIGHT}', '320')}
                    epg.update({channel['channelId'] + str(startts) : epg_item})
    return epg

# def get_item_epg(id):
#     session = Session()
#     post = {"language":"ces","ks":session.ks,"filter":{"objectType":"KalturaSearchAssetFilter","orderBy":"START_DATE_ASC","kSql":"(and epg_id:'" + str(id) + "' asset_type='epg' auto_fill= true)"},"pager":{"objectType":"KalturaFilterPager","pageSize":500,"pageIndex":1},"clientTag":clientTag,"apiVersion":apiVersion}
#     return epg_api(post = post, key = 'id')[id]

# def epg_api(post, key, no_md_title = False):
#     epg = {}
#     result = oneplay_list_api(post = post, type = 'EPG', nolog = True)
#     channels = Channels()
#     channels_list = channels.get_channels_list('id', visible_filter = False)            
#     for item in result:
#         if (item['objectType'] == 'KalturaProgramAsset' or item['objectType'] == 'KalturaRecordingAsset') and 'linearAssetId' in item:
#             id = item['id']
#             channel_id = item['linearAssetId']
#             title = item['name']
#             if 'description' in item:
#                 description = item['description']
#             else:
#                 description = ''
#             startts = item['startDate']
#             endts = item['endDate']

#             cover = ''
#             poster = ''
#             imdb = ''
#             year = ''
#             contentType = ''
#             original = ''
#             genres = []
#             cast = []
#             directors = []
#             writers = []
#             country = ''

#             ratios = {'2x3' : '/height/720/width/480', '3x2' : '/height/480/width/720', '16x9' : '/height/480/width/853'}
#             if len(item['images']) > 0:
#                 poster = item['images'][0]['url'] + ratios[item['images'][0]['ratio']]
#             if len(item['images']) > 1:
#                 cover = item['images'][1]['url'] + ratios[item['images'][1]['ratio']]
#             if 'original_name' in item['metas']:
#                 original = item['metas']['original_name']['value']
#             if 'imdb_id' in item['metas']:
#                 imdb = str(item['metas']['imdb_id']['value'])
#             if 'Year' in item['metas']:
#                 year = str(item['metas']['Year']['value'])
#             if 'ContentType' in item['metas']:
#                 contentType = item['metas']['ContentType']['value']
#             if 'Genre' in item['tags']:
#                 for genre in item['tags']['Genre']['objects']:
#                     genres.append(genre['value'])
#             if 'PersonReference' in item['tags']:
#                 for person in item['tags']['PersonReference']['objects']:
#                     person_data = person['value'].split('|')
#                     if len(person_data) < 3:
#                         person_data.append('')
#                     cast.append((person_data[1], person_data[2]))
#             if 'Director' in item['tags']:
#                 for director in item['tags']['Director']['objects']:
#                     directors.append(director['value'])
#             if 'Writers' in item['tags']:
#                 for writer in item['tags']['Writers']['objects']:
#                     writers.append(writer['value'])
#             if 'Country' in item['tags'] and 'value' in item['tags']['Country']:
#                 country = item['tags']['Country']['value']

#             episodeNumber = -1
#             seasonNumber = -1
#             episodesInSeason = -1
#             episodeName = ''
#             seasonName = ''
#             seriesName = ''    

#             if 'EpisodeNumber' in item['metas']:
#                 episodeNumber = int(item['metas']['EpisodeNumber']['value'])
#                 if episodeNumber > 0:
#                     title = title + ' (' + str(episodeNumber) + ')'
#             if 'SeasonNumber' in item['metas']:
#                 seasonNumber = int(item['metas']['SeasonNumber']['value'])
#             if 'EpisodeInSeason' in item['metas']:
#                 episodesInSeason = int(item['metas']['EpisodeInSeason']['value'])
#             if 'EpisodeName' in item['metas']:
#                 episodeName = item['metas']['EpisodeName']['value']
#             if 'SeasonName' in item['metas']:
#                 seasonName = item['metas']['SeasonName']['value']
#             if 'SeriesName' in item['metas']:
#                 seriesName = item['metas']['SeriesName']['value']

#             if 'IsSeries' in item['metas'] and int(item['metas']['IsSeries']['value']) == 1:
#                 isSeries = True
#                 if 'SeriesID' in item['metas']:
#                     seriesId = item['metas']['SeriesID']['value']
#                 else:
#                     seriesId = ''
#             else:
#                 isSeries = False
#                 seriesId = ''
#             md = None
#             md_ids = []
#             if 'MosaicInfo' in item['tags']:
#                 session = Session()
#                 for mditem in item['tags']['MosaicInfo']['objects']:
#                     if 'MosaicProgramExternalId' in mditem['value']:
#                         md = mditem['value'].replace('MosaicProgramExternalId=', '')
#                         md_post = {"language":"ces","ks":session.ks,"filter":{"objectType":"KalturaSearchAssetFilter","orderBy":"START_DATE_ASC","kSql":"(and IsMosaicEvent='1' MosaicInfo='mosaic' (or externalId='" + str(md) + "'))"},"pager":{"objectType":"KalturaFilterPager","pageSize":200,"pageIndex":1},"clientTag":clientTag,"apiVersion":apiVersion}
#                         if no_md_title == False:
#                             md_epg = oneplay_list_api(post = md_post, type = 'multidimenze', nolog = True)
#                             if len(md_epg) > 0 and 'name' in md_epg[0]:
#                                 title = md_epg[0]['name']

#             if 'MosaicChannelsInfo' in item['tags']:
#                 for mditem in item['tags']['MosaicChannelsInfo']['objects']:
#                     if 'ProgramExternalID' in mditem['value']:
#                         md_ids.append(mditem['value'].split('ProgramExternalID=')[1])
#             epg_item = {'id' : id, 'title' : title, 'channel_id' : channel_id, 'description' : description, 'startts' : startts, 'endts' : endts, 'cover' : cover, 'poster' : poster, 'original' : original, 'imdb' : imdb, 'year' : year, 'contentType' : contentType, 'genres' : genres, 'cast' : cast, 'directors' : directors, 'writers' : writers, 'country' : country, 'episodeNumber' : episodeNumber, 'seasonNumber' : seasonNumber, 'episodesInSeason' : episodesInSeason, 'episodeName' : episodeName, 'seasonName' : seasonName, 'seriesName' : seriesName, 'isSeries' : isSeries, 'seriesId' : seriesId, 'md' : md, 'md_ids' : md_ids}
#             if key == 'startts':
#                 epg.update({startts : epg_item})
#             elif key == 'channel_id':
#                 epg.update({channel_id : epg_item})
#             elif key == 'id':
#                 epg.update({id : epg_item})
#             elif key == 'startts_channel_number':
#                 if channel_id in channels_list:
#                     epg.update({int(str(startts)+str(channels_list[channel_id]['channel_number']).zfill(5))  : epg_item})
#     return epg

def epg_listitem(list_item, epg, icon):
    cast = []
    directors = []
    writers = []
    genres = []

    kodi_version = get_kodi_version()
    if kodi_version >= 20:
        infotag = list_item.getVideoInfoTag()
        infotag.setMediaType('movie')
    else:
        list_item.setInfo('video', {'mediatype' : 'movie'})
    if 'cover' in epg and len(epg['cover']) > 0:
        if 'poster' in epg and len(epg['poster']) > 0:
            if icon == '':
                icon = epg['poster']
            list_item.setArt({'poster': epg['poster'], 'icon': icon})
        else:
            if icon == '':
                icon = epg['cover']
            list_item.setArt({'thumb': epg['cover'], 'icon': icon})
    else:
        list_item.setArt({'thumb': icon, 'icon': icon})    
    if 'description' in epg and len(epg['description']) > 0:
        if kodi_version >= 20:
            infotag.setPlot(epg['description'])
        else:
            list_item.setInfo('video', {'plot': epg['description']})
    if 'imdb' in epg and len(epg['imdb']) > 0:
        if kodi_version >= 20:
            infotag.setIMDBNumber(epg['imdb'])
        else:
            list_item.setInfo('video', {'imdbnumber': epg['imdb']})
    if 'year' in epg and len(str(epg['year'])) > 0:
        if kodi_version >= 20:
            infotag.setYear(int(epg['year']))
        else:
            list_item.setInfo('video', {'year': int(epg['year'])})
    if 'original' in epg and len(epg['original']) > 0:
        if kodi_version >= 20:
            infotag.setOriginalTitle(epg['original'])
        else:
            list_item.setInfo('video', {'originaltitle': epg['original']})
    if 'country' in epg and len(epg['country']) > 0:
        if kodi_version >= 20:
            infotag.setCountries([epg['country']])
        else:
            list_item.setInfo('video', {'country': epg['country']})
    if 'genres' in epg and len(epg['genres']) > 0:
        for genre in epg['genres']:      
          genres.append(genre)
        if kodi_version >= 20:
            infotag.setGenres(genres)
        else:
            list_item.setInfo('video', {'genre' : genres})    
    if 'cast' in epg and len(epg['cast']) > 0:
        for person in epg['cast']: 
            if kodi_version >= 20:
                cast.append(xbmc.Actor(person[0], person[1]))
            else:
                cast.append(person)
        if kodi_version >= 20:
            infotag.setCast(cast)
        else:
            list_item.setInfo('video', {'castandrole' : cast})  
    if 'directors' in epg and len(epg['directors']) > 0:
        for person in epg['directors']:      
            directors.append(person)
        if kodi_version >= 20:
            infotag.setDirectors(directors)
        else:
            list_item.setInfo('video', {'director' : directors})  
    if 'writers' in epg and len(epg['writers']) > 0:
        for person in epg['writers']:      
            writers.append(person)
        if kodi_version >= 20:
            infotag.setWriters(writers)
        else:
            list_item.setInfo('video', {'writer' : writers})  
    if 'episodeNumber' in epg and epg['episodeNumber'] != None and int(epg['episodeNumber']) > 0:
        if kodi_version >= 20:
            infotag.setEpisode(int(epg['episodeNumber']))
        else:
            list_item.setInfo('video', {'mediatype': 'episode', 'episode' : int(epg['episodeNumber'])}) 
    if 'episodeName' in epg and epg['episodeName'] != None and len(epg['episodeName']) > 0:
        if kodi_version >= 20:
            infotag.setEpisodeGuide(epg['episodeName'])
        else:
            list_item.setInfo('video', {'title' : epg['episodeName']})  
    if 'seriesName' in epg and epg['seriesName'] != None and len(epg['seriesName']) > 0:
        if kodi_version >= 20:
            infotag.addSeason(int(epg['seasonNumber']), epg['seriesName'])
        else:
            list_item.setInfo('video', {'tvshowtitle' : epg['seriesName']})  
    if 'seasonNumber' in epg and epg['seasonNumber'] != None and int(epg['seasonNumber']) > 0:
        if kodi_version >= 20:
            infotag.setSeason(int(epg['seasonNumber']))
        else:
            list_item.setInfo('video', {'season' : int(epg['seasonNumber'])})  
    return list_item

