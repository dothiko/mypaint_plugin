#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class Helloplugin:
    """ Plugin is singleton, generated once and 
    the instance called many time.
    """

   #def drag_start_cb(self, app, model, x, y, button):
   #    pass
   #
   #def drag_update_cb(self, app, model, x, y, button):
   #
   #    pass
   #
   #def drag_stop_cb(self, app, model, x, y, button):
   #    app.message_dialog("Hello, world")
   #    pass

    def activate_cb(self, app, model):
        """ Activate handler,
        """
        app.message_dialog("Hello, world")
        return None

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
    return ("Hellp plugin", None, Helloplugin())

if __name__ == '__main__':

    pass


