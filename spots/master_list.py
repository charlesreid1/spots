import sys
import os
import json
from json.decoder import JSONDecodeError
import spotipy


class MasterList(object):
    """
    Class representing a list of Spotify playlists.

    Class instances can be serialized to JSON files with
    that are lists of maps with the following keys:
    - spotify_id : Spotify ID for this playlist
    - name : name of playlist
    - description: description of playlist
    """
    def __init__(self, token, username):
        self.username = username
        self.sp = spotipy.Spotify(auth=token)

        # List of details of each playlist
        self.playlist_details = []

    def load(self, filename):
        """Load the JSON file named filename, populate the master list"""
        if not os.path.exists(filename):
            self.playlist_details = populate_master_list()
        with open(filename, 'r') as f:
            playlist_details = json.load(f)
        for playlist_detail in self.playlist_details:
            if 'spotify_id' not in playlist_detail:
                raise Exception("Error: Invalid playlist item from file %s:\n%s"%(filename, playlist_detail))
        self.playlist_details = playlist_details

    def dump(self, filename, overwrite = False):
        """Export the list of playlist details to the JSON file named filename"""
        if os.path.exists(filename) and not overwrite:
            raise FileExistsError()

        if not os.path.exists(filename):
            self.playlist_details = populate_master_list()

        for playlist_detail in self.playlist_details:
            if 'spotify_id' not in playlist_detail:
                raise Exception("Error: Invalid playlist item in memory:\n%s"%(playlist_detail))
        with open(filename, 'w') as f:
            json.dump(self.playlist_details, f, indent=4)

    def populate_master_list(self):
        """Call the Spotify API to get the master list of playlists"""
        temp_playlists = []

        # The API call gets every playlist a user follows,
        # only keep playlists made by the user.

        # Step 1: Get all playlists
        step = 200
        response = self.sp.user_playlists(
                self.username,
                limit=step,
                offset=0
        )
        temp_playlists += response['items']

        total = response['total']
        c = step
        while c < total:
            response = self.sp.user_playlists(
                    self.username,
                    limit=step,
                    offset=c
            )
            temp_playlists += response['items']
            c += step

        # Step 2: Throw away playlists not owned by user
        my_playlists = []
        for i, playlist in enumerate(temp_playlists):
            pwner = playlist['owner']['id']
            if pwner == self.username:
                pid = playlist['id']
                pname = playlist['name']
                results = self.sp.user_playlist(
                        self.username,
                        pid,
                        fields="description"
                )
                if 'description' in results.keys() and results['description'] is not None:
                    pdescr = HTMLParser().unescape(results['description'])
                else:
                    pdescr = ""

                # Save the ID, name, and description
                save = dict(
                        spotify_id = pid,
                        name = pname,
                        description = pdescr
                )
                my_playlists.append(save)

        return my_playlists

