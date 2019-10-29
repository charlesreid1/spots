#!/usr/bin/env python
"""
Spots Step 1:
Dump all Spotify playlists (master list) for the specified Spotify user.

This script uses the Spotify API to
"""
import os
import sys
import logging
import argparse
import spotipy
import spotipy.util as util

pkg_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))  # noqa
sys.path.insert(0, pkg_root)  # noqa

from secrets import CLIENT_ID, CLIENT_SECRET
from spots.master_list import MasterList


def configure_logging():
    """Create and configure logging"""
    logging.basicConfig(level=logging.DEBUG)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    # turn off annoying irrelevant stuff
    annoying = logging.getLogger("urllib3.connectionpool")
    annoying.disabled = True


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--user", required=True, help="Specify the Spotify user whose playlists will be processed"
    )
    parser.add_argument(
        "--outfile",
        required=False,
        default="master_list.json",
        help="Specify the output file for the master list",
    )
    parser.add_argument(
        "--force",
        required=False,
        default=False,
        action="store_true",
        help="Overwrite output file if it exists (default: False)",
    )
    return parser


def main(args):
    print("Creating master list for user %s..." % (args.user))
    scope = "playlist-read-private"
    uri = "http://localhost:8000"
    token = util.prompt_for_user_token(
            args.user,
            scope,
            redirect_uri=uri,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
    )
    ml = MasterList(token, args.user)

    print("Dumping master list for user %s to json..." % (args.user))
    import pdb; pdb.set_trace()
    ml.dump(args.outfile, args.force)

    print("Done.")


if __name__ == "__main__":
    configure_logging()
    parser = get_parser()

    # If no args provided, print help
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Process
    args = parser.parse_args()
    main(args)
