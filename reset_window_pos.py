#!/usr/bin/env python
# -*- coding: UTF-8 -*-

class MyResetPos(object):

    def __init__(self, app):
        workspace = app.workspace
        layouts = []
        for stack in workspace._get_tool_stacks():
            layouts.append(stack.get_paned_layout())
        self.mylocal_saved_layouts = layouts
        pass
             

    def activate_cb(self, app, model):
        """ Activate handler,
        """
        for stack_info in self.mylocal_saved_layouts:
            for pane_desc in stack_info:
                cw = pane_desc['paned']
                cw.set_position(pane_desc['pos'])
        self.app = app
        return None # returning None = DO NOT ENTER dragging mode.

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
    return ("Reset dock size", None, MyResetPos(app))


if __name__ == '__main__':

    pass


