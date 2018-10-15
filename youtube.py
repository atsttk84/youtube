#!env python
import requests
import json
import pickle
from pprint import pprint
import os

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')

class YoutubeBase:
    @staticmethod 
    def req(url, params, pageToken=None):
        params['pageToken'] = pageToken
        response = requests.get(url, params=params)
        j = json.loads(response.text)
        return j

    @staticmethod 
    def get(url, params, _get):
        res = YoutubeBase.req(url, params)
        ret = []
        _get(res, ret)
        while True:
            if not 'nextPageToken' in res:
                break
            res = YoutubeBase.req(url, params, res['nextPageToken'])
            _get(res, ret)
        pprint(ret)
        print(len(ret))
        return ret


# https://developers.google.com/youtube/v3/docs/videos?hl=ja
class YoutubeVideos(YoutubeBase):
    URL = 'https://www.googleapis.com/youtube/v3/videos'
    
    @staticmethod 
    def _get(src, dest):
        #pprint(src)
        for d in src['items']:
            video_id = d['id']
            title = d['snippet']['title']
            thumbnail = d['snippet']['thumbnails']['medium']
            dest.append({'video_id': video_id, 'title': title, 'thumbnail': thumbnail})

    @staticmethod 
    def params():
        return {'part': 'snippet','chart': 'mostPopular', 'key': GOOGLE_API_KEY, 'maxResults': 1, 'regionCode': 'jp'}

    @staticmethod 
    def run(dest):
        params = YoutubeVideos.params()
        dest.extend(YoutubeVideos.get(YoutubeVideos.URL, params, YoutubeVideos._get))

# https://developers.google.com/youtube/v3/docs/commentThreads?hl=ja
class YoutubeCommentTreads(YoutubeBase):
    URL = 'https://www.googleapis.com/youtube/v3/commentThreads'
    
    @staticmethod 
    def _get(src, dest):
        for d in src['items']:
            dest.append(d['snippet']['topLevelComment']['snippet']['textOriginal'])
            if 'replies' in d:
                for reply in d['replies']['comments']: 
                    dest.append(reply['snippet']['textOriginal'])
    @staticmethod 
    def params(video_id):
        return {'videoId': video_id, 'part': 'snippet,replies', 'key': GOOGLE_API_KEY, 'maxResults': 100}

    @staticmethod 
    def run(dest, video_id):
        params = YoutubeCommentTreads.params(video_id)
        dest[video_id] = YoutubeCommentTreads.get(YoutubeCommentTreads.URL, params, YoutubeCommentTreads._get)

if __name__ == '__main__':
    comment_dic = {}
    if os.path.exists('comment.pickle'):
        with open('comment.pickle', mode='rb') as f:
            comment_dic  = pickle.load(f)
    video_id = '1xEExHBx9O8'
    YoutubeCommentTreads.run(comment_dic, video_id)
    
    with open('comment.pickle', mode='wb') as f:
        pickle.dump(comment_dic, f)

    video_list = []
    if os.path.exists('video.pickle'):
        with open('video.pickle', mode='rb') as f:
            video_list  = pickle.load(f)
    YoutubeVideos.run(video_list)
    
    with open('video.pickle', mode='wb') as f:
        pickle.dump(video_list, f)
