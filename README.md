# mypaint_plugin
Plugin scripts, for Experimental Mypaint plugin feature

## Requirement
These plugin will work with plugin functionality of my experimental Mypaint branch ['my_build'](https://github.com/dothiko/mypaint/tree/my_build)

## How to use
Place these plugins at mypaint user-data directory, i.e. $XDG_DATA_HOME/mypaint/plugins、such as ~/.local/share/mypaint/plugins, depends on your OS and desktop environment.

And start/restart experimental version of Mypaint.

## Todo

 * Needs some interface to indicate canvas position/area to plugins.
 * Consider about security. currently, this loads any python scripts placed at plugins directory. at least 'white list' should be needed.
 * Support of the menu hierarchy.
 

----
### hello.py
Only testing, shows 'hello world' with app.message_dialog()

### mytweet.py (with mytweet.glade)
Posting tweet to Twitter, with current canvas image, without saving it and automatically resize it.
To Use this, you needs your own API KEY and API SECRET (and you must authenticate it).
Because, Tweeter requires developpers to hide API key and API secret key, but it is too difficult(or impossible) for python program.

You must write a 'apikeys.info' as json file, such as 
```
{"API_KEY": "write_the_api_key_here", "API_SECRET": "write_the_api_secret_key_here"}
```
And place it the same directory of plugin.

### reset_window_pos.py
Resetting the dock positions of Main window, as positions at startup.

This plugin is created to deal with annoying automatic resizing,
which occasionally occur at some version of Gtk3.

----
