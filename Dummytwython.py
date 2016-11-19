#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Twython:
    """ Dummy for test.
    """

    def __init__(self, API_KEY, API_SECRET, 
            OAUTH_TOKEN = None, OAUTH_TOKEN_SECRET = None):
        self._media_id = 0

    def upload_media(self, media):
        print('[DUMMY] uploading media stream (%s)...' % str(type(media)))
        ret = { 'media_id' : self._media_id }
        self._media_id += 1
        return ret

    def update_status(self, status, media_ids):
        print('[DUMMY] updating status')
        print(status)
        print('posted medias')
        for cm in media_ids:
            print(cm)

    def get_authorized_tokens(self, pin_code):
        print("pin code:")
        print(pin_code)
        if pin_code == 'MY-PIN-CODE':
            print("access to be granted")
            ret = { 'oauth_token' : 'test-oauth-token',
                    'oauth_token_secret' : 'SECRET!!' }
        else:
            print("access rejected.")
            ret = {}
        return ret

    def get_authentication_tokens(self):
        ret = { 'auth_url' : 'http://sonna_siteha_nai.com',
                'oauth_token' : 'tmp-oauth-token',
                'oauth_token_secret' : 'tmp SECRET!!' 
                }
        return ret

if __name__ == '__main__':

    pass


