'''
Created on Dec 20, 2016

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
from config import PLAYLIST_ROOT_FOLDER
os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
    

def get_system_logged_in_user_info():
    """
    This will get the currently system logged in username and homepath
    """
    username= os.environ["LOGNAME"]
    homepath = os.path.expanduser("~"+username+"/")
    return username, homepath


def get_app_credentials():
    """
    This function will run the credential flow for the google data api. In case a permission deined error
    is generated, you must change the file permissions in httplib2 package as follows:
    'sudo chmod o+r /Library/Python/2.7/site-packages/httplib2-0.9.2-py2.7.egg/httplib2/cacerts.txt'
    The return object is a credentials objects that can be used subequently in api calls.
    """
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
    """
    This is a utility function to retreive a youtube Resourse objects based on the supplied credentials object.
    """
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    http=credentials.authorize(httplib2.Http()))
    return youtube


def get_my_channel_id(youtube):
    """
    This is a quick and dirty method to return the main channel of the app user
    """
    result = youtube.channels().list(part='id', mine=True).execute()
    channel_id = result.get('items', [{}])[0].get('id', None)
    return channel_id


def get_playlists_data(youtube, channel_id):
    """
    This function returns the info of all playlists of the channel with the supplied channel_id
    """
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
    """
    This function retreives a playlist id based on the supplied channel_id and playlist_title arguments.
    It is assumed that playlist titles are unique.
    """
    items = get_playlists_data(youtube, channel_id)
    for item in items:
        if item.get('title') == playlist_title:
            return item.get('id')
    return None


def get_playlist_videos(youtube, playlist_id):
    """
    This function retreives a list of all video data in the playlist with the supplied playlist_id
    """
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


def download_video_as_mp3(video_url, target_path, ordinal_number=None):
    """
    This function will download the supplied video_url into an mp3 file in the supplied target_path.
    """
    if ordinal_number is None:
        ordinal_number = ''
    else:
        ordinal_number = '%s_' % ('0'* (4 - len(str(ordinal_number))) + str(ordinal_number),)
    download_command = 'youtube-dl --no-playlist --format worstaudio --extract-audio --audio-format mp3 --audio-quality 5 -o "%s/%s%%(title)s.%%(ext)s" %s'
    download_command = download_command % (target_path, ordinal_number, video_url)
    os.system(download_command)
        

def download_playlist_audio(videos, target_path):
    """
    This function will simply download all the vedios specified in videos and convert them in to mp3
    into the supplied target_path
    """
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
            download_video_as_mp3(video_url, target_path, ordinal_number=ith + 1)
            meta[video_url] = 'downloaded'
            pickle.dump(meta, open(meta_path, 'wb'))
        else:
            print 'skipping audio of video_url "%s", already downloaded' % video_url




if __name__ == '__main__':
    print 'commencing...\n\n'
    PLAYLIST_TITLE = 'Eckhart Tolle'
    credentials = get_app_credentials()
    youtube = get_youtube_api_object(credentials)
    channel_id = get_my_channel_id(youtube)
    playlist_id = get_playlist_id_by_title(youtube, channel_id, PLAYLIST_TITLE)
    videos = get_playlist_videos(youtube, playlist_id)
    target_path = os.path.join(PLAYLIST_ROOT_FOLDER, PLAYLIST_TITLE)
    download_playlist_audio(videos, target_path)
    print '\n\n...done'
    
    
    
        
    
    
    