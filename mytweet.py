#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import sys
import json
import time
      
import gi
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import GdkPixbuf
import cairo

MAX_WIDTH = 600
MAX_LENGTH = 140
CFGFILE = 'mytwitter.json'
AUTH_FILE="tokens.info"
API_KEY="S4yiHBJiOE0C7T4nuOQuitkGY",
API_SECRET="vEtZxALxvvteNMlNYd3dfOhvH5ZDtOlryHLhNONz0GdrNLIRrH"

class Mytweetplugin:

    def __init__(self, base_dir):
        self._grid_base = None
        self._pixbuf = None
        self._base_dir = base_dir
        cfg_file = os.path.join(base_dir, CFGFILE)
        if os.path.exists(cfg_file):
            with open(cfg_file, 'r') as ifp:
                self.conf = json.load(ifp)
        else:
            self.conf = {}

        self._written = False

    def _build_ui(self):
        if self._grid_base is not None:
            return
        self._updating_ui = True
        builder_xml = os.path.splitext(__file__)[0] + ".glade"
        builder = Gtk.Builder()
        builder.add_from_file(builder_xml)
        builder.connect_signals(self)
        self._grid_base = builder.get_object("base_grid")
        self._pane = builder.get_object("paned_view")
        self._area_preview = builder.get_object("area_preview")
        self._textview_tweet = builder.get_object("textview_tweet")
        self._entry_tags = builder.get_object("entry_tags")
        dlg = builder.get_object("mytweet_dialog")

        w = self.conf.get('dialog.width', dlg.get_allocation().width)
        h = self.conf.get('dialog.height', dlg.get_allocation().height)
        dlg.set_size_request(w, h)
        self._dialog = dlg

        self._dialog_ask = builder.get_object("dialog_ask")

        self._setup_dialog_pincode(builder)

        self._updating_ui = False
    
    def run(self, pixbuf):
        self._pixbuf = pixbuf
        self._build_ui()
        self._dialog.run()

    def write_conf(self, key, value):
        if (not key in self.conf) or self.conf[key] != value:
            self.conf[key] = value
            self._written = True

    def end(self):
        dlg = self._dialog
        w = dlg.get_allocation().width
        h = dlg.get_allocation().height

        self.write_conf('dialog.width', w)
        self.write_conf('dialog.height', h)
        if self._written:
            cfg_file = os.path.join(base_dir, CFGFILE)
            with open(cfg_file, 'w') as ofp:
                json.dump(self.conf, ofp)

        dlg.destroy()
        self._dialog_ask.destroy()
        self._dialog_pincode.destroy()
        self._grid_base = None

    def area_preview_draw_cb(self, widget, cr):
        
        ww = widget.get_allocation().width
        wh = widget.get_allocation().height
        cr.translate(ww / 2, wh / 2)
        view_aspect = ww / float(wh)

        w = self._pixbuf.get_width()
        h = self._pixbuf.get_height()
        pic_aspect = w / float(h)

        if view_aspect >= 1.0:
            # vert based(vertically small) view
            ratio = float(wh) / h
        else:
            # horz based(horz small) view
            ratio = float(ww) / w

        cr.scale(ratio, ratio)

        x = -w/2.0
        y = -h/2.0

        Gdk.cairo_set_source_pixbuf(cr, self._pixbuf, x , y)
        cr.rectangle(x, y, w, h)
        cr.paint()

    def submit_clicked_cb(self, widget):
        """ Caution: all texts once convert into UCS-2
        """
        tag_src = self._entry_tags.get_text().decode('utf-8')
        if tag_src != "":
            tags = [ "#%s" % x for x in tag_src.split()]

        buf = self._textview_tweet.get_buffer()
        start = buf.get_iter_at_offset(0)
        end = buf.get_iter_at_offset(-1)
        tweet_msg = buf.get_text(start, end, False).decode('utf-8')
        for cur_tag in tags:
            tweet_msg += " "
            tweet_msg += cur_tag
        if len(tweet_msg) > MAX_LENGTH:
            self.show_message("ERROR: Your tweet is %s letters.\n exceeds max %d letters so cannot send." % (len(tweet_msg),MAX_LENGTH))
        else:
            self.tweet(tweet_msg)
            self.end()

    def cancel_clicked_cb(self, widget):
        self.end()


    def activate_cb(self, app, model):
        """ Activate handler,
        """
        self.app = app
        self.run()
        return None


    def tweet(self, msg, pixbuf_list):
        try:
           #from twython import Twython
            from Dummytwython import Twython
            auth_file = os.path.join(self._base_dir, AUTHFILE)
            with open(auth_file, 'r') as ifp:
                auth = json.load(ifp)
                OAUTH_TOKEN = auth['oauth_token']
                OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
            tw = Twython(API_KEY, API_SECRET,
                         OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        except IOError as e:
           #self.show_message("There is no authentication file.\n you might need to get PIN code.proceed?")
            self.ask_auth()
        except ImportError as e:
            self.show_message("ERROR: cannot import Twython. Tweet failed.")
        except Exception as e:
            self.show_message(str(e))
        else:
            media_ids = []
            if media_file:
                if type(media_file) == str:
                    media_file = [media_file, ]
                for cm in pixbuf_list:
                   #if os.path.exists(cm):
                   #    pic_fp = open(cm, 'rb')
                   #    response = tw.upload_media(media = pic_fp)
                   #    media_ids.append(response['media_id'])
                   #    print('media %s has uploadded.wait for next media...' % cm)
                   #    time.sleep(1)
                   #else:
                   #    print('[ERROR] media %s does not exist!!' % cm)
                    response = tw.upload_media(media = pic_fp)
                    media_ids.append(response['media_id'])
                    time.sleep(1)

            tw.update_status(status = msg, media_ids = media_ids)


    def show_message(self, msg):
        if hasattr(self, "app"):
            self.app.message_dialog(msg)
        else:
            print(msg)

    ## Asking dialog related

    def ask_auth(self):
        self._dialog_ask.run()

    def button_ask_yes_cb(self, widget):
        self.run_pincode()
        self._dialog_ask.close()

    def button_ask_no_cb(self, widget):
        self._dialog_ask.close()

    ## PINCode dialog related


    def _setup_dialog_pincode(self, builder):
        self._entry_url = builder.get_object('entry_url')
        self._entry_pincode = builder.get_object('entry_pincode')
        self._dialog_pincode = builder.get_object('dialog_pincode')
        self._dialog_pincode.set_size_request(600, 300)

    def run_pincode(self):
        tw = Twython(API_KEY, API_SECRET)
        self.auth = tw.get_authentication_tokens()

        self._entry_url = self.auth['auth_url']
        self._dialog_pincode.run()

    def button_pincode_ok_cb(self, widget):
        pin_code = self._entry_pincode.get_text().strip()
        if pin_code != "":
            tw = Twython(API_KEY, API_SECRET,
                    auth['oauth_token'], auth['oauth_token_secret'])
            final = tw.get_authorized_tokens(pin_code)
            auth_file = os.path.join(self._base_dir, AUTHFILE)
            with open(auth_file, 'w') as ofp:
                json.dump(final, ofp)
            self.show_message("Authenticate completed. Please retry tweet.")
            self._dialog_pincode.close()
        else:
            self.show_message("You need to get PIN code from the URL and paste it for authentication.")
    
    def button_pincode_cancel_cb(self, widget):
        self._dialog_pincode.close()

   #def get_token(self):
   #    tw = Twython(API_KEY, API_SECRET)
   #    auth = tw.get_authentication_tokens()
   #    print("----------------------------------------")
   #    print("Now, you must open the url")
   #    print(auth['auth_url'])
   #    print("and get PIN code, then input that code here:")
   #    pin_code = raw_input("PIN code? : ")
   #    # IMPORTANT: Re-generate twtter instance with
   #    # returned temporary auth information
   #    tw = Twython(API_KEY, API_SECRET,
   #            auth['oauth_token'], auth['oauth_token_secret'])
   #    final = tw.get_authorized_tokens(pin_code)
   #   #print(final)
   #    auth_file = os.path.join(self._base_dir, AUTHFILE)
   #    with open(auth_file, 'w') as ofp:
   #        json.dump(final, ofp)
   #    self.show_message("**** COMPLETED - then, restart oneshottw - ****")


def register(app):
    """ Called from mypaint at initialize,
    to register plugin.
    :param app: application instance of mypaint.

    :return : a tuple of 
                (string for menu label, 
                 icon pixbuf(might be None), 
                 plugin instance)
    :rtype tuple:
    """
    plugin_dir = os.path.join(app.state_dirs.user_data, 'plugins')
   #pixbuf = GdkPixbuf.Pixbuf.new_from_file(os.path.join(plugin_dir, 'test.jpg'))
    return ("Twitter post", None, Mytweetplugin(plugin_dir))

if __name__ == '__main__':

    pixbuf = GdkPixbuf.Pixbuf.new_from_file('test.jpg')
    t = Mytweetplugin("")
    t.run(pixbuf)
    pass


