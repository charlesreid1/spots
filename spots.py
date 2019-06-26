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


def main():
    """
    make the static site
    """

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        logging.info("Whoops, need your username!")
        logging.info("usage: python spots.py [username]")
        sys.exit()

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

    ## Step 1: dump to json
    #ml.export_ids_list_to_file()

    # Step 2: edit the json file directly...

    # Step 3: create the static site
    logging.debug('calling MasterList.static_site()')
    ml.static_site('site')


if __name__=="__main__":
    main()

