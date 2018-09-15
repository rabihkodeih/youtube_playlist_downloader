'''
Created on Dec 20, 2016

@author: rabihkodeih
'''

import os
from api import get_app_credentials, report_videos, reset_downloads,\
    show_all_playlists
from api import get_youtube_api_object
from api import get_my_channel_id
from api import get_playlist_id_by_title
from api import get_playlist_videos
from api import download_playlist_audio
from config import PLAYLIST_ROOT_FOLDER

os.environ['PATH'] = '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'


if __name__ == '__main__':

    print 'commencing...\n\n'
#     PLAYLIST_TITLES = ['Actualized',
#                        'Mounir-Al-Khabbaz',
#                        'Eckhart Tolle',
#                        'Khakani',
#                        'Leo-Awakening',
#                        'osho',
#                        'rock-love-songs',
#                        'Slow-Music']
    PLAYLIST_TITLES = ['Slow-Music']
    AUDIO_QUALITY = 'worstaudio'  # 'bestaudio', 'worstaudio'
    USE_ORDINAL_NUMBERS = False

    credentials = get_app_credentials()
    youtube = get_youtube_api_object(credentials)
    channel_id = get_my_channel_id(youtube)
    for playlist_title in PLAYLIST_TITLES:
        # show_all_playlists(youtube, channel_id);exit()
        playlist_id = get_playlist_id_by_title(youtube, channel_id,
                                               playlist_title)
        videos = get_playlist_videos(youtube, playlist_id)
        target_path = os.path.join(PLAYLIST_ROOT_FOLDER, playlist_title)
        download_playlist_audio(videos, target_path, AUDIO_QUALITY,
                                USE_ORDINAL_NUMBERS)
        # report_videos(videos)
        # reset_downloads(videos, target_path, starting_ordinal_number=17)
    print('\n\n...done')
