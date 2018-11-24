# shows audio analysis for the given track

from __future__ import print_function    # (at top of module)
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import os
import time
import json
import spotipy
import spotipy.util as util

from secrets import CLIENT_ID, CLIENT_SECRET

scope = "playlist-read-private"
uri = "http://localhost:8000"
username = 'charlesreid1'
client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID,client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

if len(sys.argv) > 1:
    tid = sys.argv[1]
else:
    tid = 'spotify:track:4TTV7EcfroSLWzXRY6gLv6'

start = time.time()
analysis = sp.audio_analysis(tid)
delta = time.time() - start
print(json.dumps(analysis, indent=4))
print ("analysis retrieved in %.2f seconds" % (delta,))

