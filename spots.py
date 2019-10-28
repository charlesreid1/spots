#!/usr/bin/env python
"""
Central entrypoint for spots
"""
import sys
import logging

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # noqa
sys.path.insert(0, pkg_root)  # noqa

import spots

from src import 

from spots_objects import SpotifyMasterList

import spotipy
import spotipy.util as util

from secrets import CLIENT_ID, CLIENT_SECRET



logging.basicConfig(level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# turn off annoying irrelevant stuff
annoying = logging.getLogger('urllib3.connectionpool')
annoying.disabled=True


def main():

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        logging.info("Whoops, need your username!")
        logging.info("usage: python spots.py [username]")
        sys.exit()
    
    ml = make_master_list(username)

    # Step 1: dump to master list json
    ml.export_ids_list_to_file()

    # Step 2: edit the master list json file directly...

    ## Step 3: create the static site
    ## (this will make master list details json file)
    #logging.debug('calling MasterList.static_site()')
    #ml.static_site('site')


def make_master_list(username):
    # Spotify API permission scope
    scope = "playlist-read-private"
    
    # Spotify API callback URL
    uri = "http://localhost:8000"

    logging.debug("getting token")
    token = util.prompt_for_user_token(
            username,
            scope,
            redirect_uri=uri,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
    )
    logging.debug("done getting token")

    logging.debug("creating spotify master list")
    ml = SpotifyMasterList(token,username)
    logging.debug("done creating spotify master list")

    return ml


if __name__=="__main__":
    main()

