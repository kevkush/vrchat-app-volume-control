# vrchat-app-volume-control

Don't wanna pull up your overlay to turn down the crazy EDC set you're listening to on youtube? Can't be bothered to click that little Spotify volume control? Vrchat audio menu too slow to access?

Now you can control any process' volume from inside VRChat, in your expressions menu! Just map the control of an unused/blank float parameter to a process name using this script, and the per-app volume control will be set accordingly. It's a little python script that sits and listens for VRChat's OSC to spit out those specifically named float parameters and changes app volume. It even strips out VRCFury parameter renaming prefixes (optional) if thats something you use. Recommended to use VRCFury to create the component, and their built in parameter compressor (thanks sent) to save parameter space.

PREREQUISITES: python, python-osc, pycaw, comtypes

USAGE:

create an actionless float parameter in VRC controlled w/ radial (recommended to use VRCfury as shown in the screenshots to make this easy)
map the same parameter name to a process in the top of the script
volume control go brrrr

Script assumes a smol amount of python/OSC/unity capability - use, modify, enjoy!
