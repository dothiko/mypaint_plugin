#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Twython:
    """ Dummy for test.
    """

    def __init__(self, API_KEY, API_SECRET, 
            OAUTH_TOKEN = None, OAUTH_TOKEN_SECRET = None):
        self._media_id = 0

    def upload_media(self, media_fp):
        print('uploading media stream...')
        self._media_id += 1
        return self._media_id

    def update_status(self, status, media_ids):
        print('updating status')
        print(status)
        print('posted medias')
        for cm in media_ids:
            print(cm)

    def get_authorized_tokens(self, pin_code):
        print("pin code:")
        print(pin_code)
        print("access to be granted")
        ret = { 'oauth_token' : 'test-oauth-token',
                'oauth_token_secret' : 'SECRET!!' }
        return ret

    def get_authentication_tokens(self):
        ret = { 'auth_url' : 'http://sonna_siteha_nai.com',
                }
        return ret

if __name__ == '__main__':

    pass


