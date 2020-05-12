# include json
# couple of lines
# editable by human

import sys
from spots_objects import SpotifyMasterList

import spotipy
import spotipy.util as util

from secrets import CLIENT_ID, CLIENT_SECRET

import logging


logging.basicConfig(level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# turn off annoying irrelevant stuff
annoying = logging.getLogger('urllib3.connectionpool')
annoying.disabled=True


def usage():
    logging.info("Whoops, need your username and an action!")
    logging.info("usage: python spots.py [username] [action]")
    logging.info("action = extract | create")
    sys.exit()


def main():

    if len(sys.argv) != 3:
        usage()

    username = sys.argv[1]
    action = sys.argv[2]

    if action not in ['extract', 'create']:
        usage()
    
    ml = make_master_list(username)

    if action == "extract":
        # Step 1: extract api info to master list json
        ml.export_ids_list_to_file()

    # Step 2: edit the master list json file directly...

    if action == "create":
        # Step 3: create the static site
        # (this will make master list details json file)
        logging.debug('calling MasterList.static_site()')
        ml.static_site()


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

