'''
Created on Dec 20, 2016

@author: rabihkodeih
'''

import os
from api import get_app_credentials
from api import get_youtube_api_object
from api import get_my_channel_id
from api import get_playlist_id_by_title
from api import get_playlist_videos
from api import download_playlist_audio
from config import PLAYLIST_ROOT_FOLDER

os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
    


if __name__ == '__main__':
    print 'commencing...\n\n'
    PLAYLIST_TITLE = 'Thrash Metal 1' # 'Thrash Metal 1', 'Eckhart Tolle'
    AUDIO_QUALITY = 'bestaudio' # 'bestaudio', 'worstaudio'
    credentials = get_app_credentials()
    youtube = get_youtube_api_object(credentials)
    channel_id = get_my_channel_id(youtube)
    playlist_id = get_playlist_id_by_title(youtube, channel_id, PLAYLIST_TITLE)
    videos = get_playlist_videos(youtube, playlist_id)
    target_path = os.path.join(PLAYLIST_ROOT_FOLDER, PLAYLIST_TITLE)
    download_playlist_audio(videos, target_path, AUDIO_QUALITY)
    print '\n\n...done'
    
    
    
        
    
    
    