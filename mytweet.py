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
AUTHFILE="tokens.info"
APIKEYFILE="apikeys.info"

class Mytweetplugin:
    """ My tweet plugin
    To post a tweet with current canvas image directly,
    without save it into filesystem.

    NEEDED MODULES:
        Python-Imaging (a.k.a PIL)

    HOW TO DRY-RUN:
        
        you can test this plugin with dry-run state, which means
        actually does not update status(post tweet).

        it is simple, to set self.app attribute as None
        before self.tweet() method is called.
        or completely remove self.app attribute.

    """

    ## class constants

    MAX_TWITTER_COUNT = 140

    def __init__(self):
        self._grid_base = None
        self._pixbuf = None
        self._base_dir = os.path.dirname(__file__)
        cfg_file = os.path.join(self._base_dir, CFGFILE)
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

        # Setting Textview/buffer
        view = builder.get_object("textview_tweet")
        buf = view.get_buffer()
        self._warn_tag = buf.create_tag(tag_name = "exceed_warning", background="red")
        buf.connect("changed", self.textbuffer_changed_cb)

        self._textview_tweet = view



        self._entry_tags = builder.get_object("entry_tags")
        dlg = builder.get_object("mytweet_dialog")

        w = self.conf.get('dialog.width', dlg.get_allocation().width)
        h = self.conf.get('dialog.height', dlg.get_allocation().height)
        dlg.set_size_request(w, h)
        self._dialog = dlg

        self._dialog_ask = builder.get_object("dialog_ask")

        self._setup_dialog_pincode(builder)

        self._updating_ui = False

    @property
    def is_dry_run(self):
        return not hasattr(self, 'app') or self.app == None
    
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
            cfg_file = os.path.join(self._base_dir, CFGFILE)
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
        tags = None
        if tag_src != "":
            tags = [ "#%s" % x for x in tag_src.split()]

        buf = self._textview_tweet.get_buffer()
        start = buf.get_iter_at_offset(0)
        end = buf.get_iter_at_offset(-1)
        tweet_msg = buf.get_text(start, end, False).decode('utf-8')
        if tags:
            for cur_tag in tags:
                tweet_msg += " "
                tweet_msg += cur_tag
        if len(tweet_msg) > MAX_LENGTH:
            self.show_message("ERROR: Your tweet is %s letters.\n exceeds max %d letters so cannot send." % (len(tweet_msg),MAX_LENGTH))
        else:
            self.tweet(tweet_msg, [self._pixbuf, ])
            self.end()

    def cancel_clicked_cb(self, widget):
        self.end()


    def activate_cb(self, app, model):
        """ Activate handler,
        """
        self.app = app

        root = model.layer_stack
        if model.get_frame_enabled():
            bbox = model.get_frame()
        else:
            bbox = root.get_bbox()

        pixbuf = root.render_as_pixbuf(*bbox, alpha=False)

        self.run(pixbuf) 
        return None # returning None = DO NOT ENTER dragging mode.

    def tweet(self, msg, pixbuf_list):
        try:
           #if hasattr(self, 'app') and self.app != None:
            if not self.is_dry_run:
                from twython import Twython
               #from Dummytwython import Twython
                self.Twython = Twython
            else:
                # for 
                from Dummytwython import Twython
                global AUTHFILE
                AUTHFILE="tokens2.info"
                self.Twython = Twython
                print('*** DRY-RUN TEST initiated ***')
            auth_file = os.path.join(self._base_dir, AUTHFILE)
            # Load Authenticate infomation file
            with open(auth_file, 'r') as ifp:
                auth = json.load(ifp)
                self.auth = auth
                OAUTH_TOKEN = auth['oauth_token']
                OAUTH_TOKEN_SECRET = auth['oauth_token_secret']
            # Load API Key infomation file
            key_file = os.path.join(self._base_dir, APIKEYFILE)
            if os.path.exists(key_file):
                with open(key_file, 'r') as ifp:
                    auth = json.load(ifp)
                    self.auth = auth
                    API_KEY = auth['API_KEY']
                    API_SECRET= auth['API_SECRET']
                tw = self.Twython(API_KEY, API_SECRET,
                             OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
            else:
                self.show_message("You need your API key(API_KEY) and API secret(API_SECRET) as json file %s" % key_file)
                self.end()
        except IOError as e:
            # Authenticate file does not exist.
            # so Request PIN Codes.
            self.ask_auth()
        except ImportError as e:
            self.show_message("ERROR: cannot import Twython. Tweet failed.")
        except Exception as e:
            self.show_message(str(e))
        else:
            from PIL import Image
            from StringIO import StringIO
            def convert_image(pixbuf):
                width,height = pixbuf.get_width(),pixbuf.get_height()
                print('---start---')
                print((width,height))
                print(pixbuf.get_rowstride())

                if pixbuf.get_has_alpha():
                    channel_cnt = 4
                    channel_str = "RGBA"
                else:
                    channel_cnt = 3
                    channel_str = "RGB"

                if pixbuf.get_rowstride() > width * channel_cnt: 
                    # Workaround for rowstride related glitches.
                    p = ''
                    i = 0
                    pixels = pixbuf.get_pixels()
                    for y in xrange(height):
                        p += pixels[i:i + width * channel_cnt]
                        i += pixbuf.get_rowstride()
                    outimg = Image.frombytes(channel_str,(width, height), p)
                else:
                    outimg = Image.frombytes(channel_str,(width,height),pixbuf.get_pixels() )

                if width > MAX_WIDTH:
                    wpercent = (MAX_WIDTH / float(width))
                    height = int(height * float(wpercent))
                    if hasattr(Image,'LANCZOS'):
                        filter=Image.LANCZOS
                    else:
                        filter=Image.CUBIC
                    outimg = outimg.resize((MAX_WIDTH, height), 
                            filter)

                image_io = StringIO()
                outimg.save(image_io, format='JPEG', 
                        quality=90, optimize=True)
                image_io.seek(0)

                # XXX Testing codes, for dry-run
                if self.is_dry_run:
                    if not hasattr(self, 'dry_run_idx'):
                        self.dry_run_idx = 0
                    else:
                        self.dry_run_idx += 1
                    idx = self.dry_run_idx
                    outimg.save('/tmp/dryrun_converted-%d.jpg' % idx, format='JPEG', 
                            quality=90, optimize=True)

                return image_io

            media_ids = []
            for cm in pixbuf_list:
                pic_io = convert_image(cm)
                response = tw.upload_media(media = pic_io)
                media_ids.append(response['media_id'])
                del pic_io
                time.sleep(1)
            
            tw.update_status(status = msg, media_ids = media_ids)
            self.show_message("Successfully tweet the message")

    def show_message(self, msg):
        if hasattr(self, "app"):
            self.app.message_dialog(msg)
        else:
            print(msg)

    ## Asking dialog related

    def ask_auth(self):
        self._dialog_ask.run()

    def button_ask_yes_clicked_cb(self, widget):
        self.run_pincode()
        self._dialog_ask.close()

    def button_ask_no_clicked_cb(self, widget):
        self._dialog_ask.close()

    def textbuffer_changed_cb(self, buf):  
        if buf.get_char_count() > self.MAX_TWITTER_COUNT:
            start_iter = buf.get_iter_at_offset(self.MAX_TWITTER_COUNT)
            end_iter = buf.get_iter_at_offset(buf.get_char_count())
            buf.apply_tag(self._warn_tag, start_iter, end_iter)
            pass

    ## PINCode dialog related


    def _setup_dialog_pincode(self, builder):
        self._entry_url = builder.get_object('entry_url')
        self._entry_pincode = builder.get_object('entry_pincode')
        self._dialog_pincode = builder.get_object('dialog_pincode')
        self._dialog_pincode.set_size_request(600, 300)

    def run_pincode(self):
        tw = self.Twython(API_KEY, API_SECRET)
        self.auth = tw.get_authentication_tokens()

        self._entry_url.set_text(self.auth['auth_url'])
        self._dialog_pincode.run()

    def button_pincode_ok_clicked_cb(self, widget):
        pin_code = self._entry_pincode.get_text().strip()
        if pin_code != "":
            auth = self.auth
            tw = self.Twython(API_KEY, API_SECRET,
                    auth['oauth_token'], auth['oauth_token_secret'])
            final = tw.get_authorized_tokens(pin_code)
            if 'oauth_token' in final and 'oauth_token_secret' in final:
                auth_file = os.path.join(self._base_dir, AUTHFILE)
                with open(auth_file, 'w') as ofp:
                    json.dump(final, ofp)
                self.auth = final
                self.show_message("Authenticate completed. Please retry tweet.")
                self._dialog_pincode.close()
            else:
                self.show_message("Authenticate failed. PIN code might be wrong.Please confirm it and retry.")

        else:
            self.show_message("You need to get PIN code from the URL and paste it for authentication.")
    
    def button_pincode_cancel_clicked_cb(self, widget):
        self._dialog_pincode.close()

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
    return ("Twitter post", None, Mytweetplugin())

if __name__ == '__main__':

    pixbuf = GdkPixbuf.Pixbuf.new_from_file('test_odd.jpg')
    t = Mytweetplugin()
    t.run(pixbuf)
    pass


