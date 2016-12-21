'''
Created on Dec 21, 2016

@author: rabihkodeih
'''

import httplib2
import os
import sys
import cPickle as pickle
from pprint import pprint  # @UnusedImport
    

from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow
from config import CLIENT_SECRETS_FILE
from config import YOUTUBE_API_SERVICE_NAME
from config import YOUTUBE_API_VERSION
from config import MISSING_CLIENT_SECRETS_MESSAGE
from config import YOUTUBE_READ_WRITE_SCOPE
    

def get_system_logged_in_user_info():
    '''
    This will get the currently system logged in username and homepath.
    returns: (username, homepath)
    '''
    username= os.environ["LOGNAME"]
    homepath = os.path.expanduser("~"+username+"/")
    return username, homepath


def get_app_credentials():
    '''
    This function will run the credential flow for the google data api. In case a permission deined error
    is generated, you must change the file permissions in httplib2 package as follows:
    'sudo chmod o+r /Library/Python/2.7/site-packages/httplib2-0.9.2-py2.7.egg/httplib2/cacerts.txt'
    returns: a credentials object that can be used in subsequent api calls
    '''
    flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, 
                                   message=MISSING_CLIENT_SECRETS_MESSAGE, 
                                   scope=YOUTUBE_READ_WRITE_SCOPE)
    storage = Storage("%s-oauth2.json" % sys.argv[0])
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        flags = argparser.parse_args()
        credentials = run_flow(flow, storage, flags)
    return credentials
    

def get_youtube_api_object(credentials):
    '''
    This is a utility function to retreive a youtube resourse objects based on user credentials.
    @param credentials: the credentials object
    returns: a youtube resource object
    '''
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    http=credentials.authorize(httplib2.Http()))
    return youtube


def get_my_channel_id(youtube):
    '''
    This function returns the main channel id of the authorizing user.
    @param youtube: the main youtube resource object
    returns: the channel id as a string
    '''
    result = youtube.channels().list(part='id', mine=True).execute()
    channel_id = result.get('items', [{}])[0].get('id', None)
    return channel_id


def get_playlists_data(youtube, channel_id):
    '''
    This function returns the info of all playlists of a channel.
    @param youtube: the main youtube resource object
    @param channel_id: the channel id
    returns: a list of playlist info objects
    '''
    result = youtube.playlists().list(part='snippet', channelId=channel_id).execute()
    playlists_data = []
    items = result.get('items', [])
    for item in items:
        data = {}
        data['id'] = item.get('id', None)
        data['title'] = item.get('snippet', {}).get('title', None) 
        playlists_data.append(data)
    return playlists_data


def get_playlist_id_by_title(youtube, channel_id, playlist_title):
    '''
    This function retreives a playlist id from a channel id and a playlist title.
    It is assumed that playlist titles are unique.
    @param youtube: the main youtube resource object
    @param channel_id: the channel id
    @param playlist_title: the playlist id
    returns: the playlist id as a string
    '''
    items = get_playlists_data(youtube, channel_id)
    for item in items:
        if item.get('title') == playlist_title:
            return item.get('id')


def get_playlist_videos(youtube, playlist_id):
    '''
    This function retreives a list of all video data in a playlist.
    @param youtube: the main youtube resource object
    @param playlist_id: the id of the playlist
    returns: [{'title':..., 'description':..., 'url':...}, ...]  
    '''
    if playlist_id is None:
        return []
    video_data = []
    next_page_token = True
    while next_page_token: 
        params = {'part': "contentDetails,snippet", 'playlistId': playlist_id}
        if next_page_token != True:
            params['pageToken'] = next_page_token
        result = youtube.playlistItems().list(**params).execute()
        next_page_token = result.get('nextPageToken', None)
        items = result.get('items', [])
        for item in items:
            video_id = item.get('contentDetails', {}).get('videoId', None)
            if video_id:
                url = 'https://www.youtube.com/watch?v=%s' % video_id
            else:
                url = None
            description = item.get('snippet', {}).get('description', None)
            title = item.get('snippet', {}).get('title', None)
            data = {'title': title, 'description':description, 'url': url}
            video_data.append(data)
    return video_data


def download_video_as_mp3(video_url, target_path, audio_quality='bestaudio', ordinal_number=None):
    '''
    This function will download the supplied video_url into an mp3 file in the supplied target_path.
    @param video_url: the full youtube url of the video to be downloaded
    @param target_path: the location of the downloaded audio file
    @param audio_quality: one of 'bestaudio' or 'worstaudio'
    @param ordinal_number: an optional 4-digit number prefix to be added to the downloaded file
    returns: None
    '''
    if ordinal_number is None:
        ordinal_number = ''
    else:
        ordinal_number = '%s_' % ('0'* (4 - len(str(ordinal_number))) + str(ordinal_number),)
    download_command = 'youtube-dl --no-playlist --format %s --extract-audio --audio-format mp3 --audio-quality 5 -o "%s/%s%%(title)s.%%(ext)s" %s'
    download_command = download_command % (audio_quality, target_path, ordinal_number, video_url)
    os.system(download_command)
        

def download_playlist_audio(videos, target_path, audio_quality):
    '''
    This function will simply download all the given videos and convert them to mp3 files.
    @param videos: a list of videos having the format: [{'title':..., 'description':..., 'url':...}, ...]
    @param target_path: the root path where all files will be written to
    @param audio_quality: one of 'bestaudio' or 'worstaudio'
    returns: None
    '''
    meta_path = os.path.join(target_path, 'meta.bin')
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    if os.path.exists(meta_path):
        meta = pickle.load(open(meta_path))
    else:
        meta = {}
    for ith, video in enumerate(videos):
        video_url = video['url']
        if video_url not in meta:
            print '%s / %s : downloading/converting audio of video_url "%s"' % (ith + 1, len(videos), video_url)
            download_video_as_mp3(video_url, target_path, audio_quality=audio_quality, ordinal_number=ith + 1)
            meta[video_url] = 'downloaded'
            pickle.dump(meta, open(meta_path, 'wb'))
        else:
            print 'skipping audio of video_url "%s", already downloaded' % video_url