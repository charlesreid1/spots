import glob
import io
import os
import json
import subprocess
from html.parser import HTMLParser
import logging

import spotipy
import spotipy.util as util

from jinja2 import Environment, PackageLoader, select_autoescape


class SpotifyMasterList(object):
    """
    This object represents a file
    containing a list of spotify
    playlists and IDs.
    
    This is a JSON file with a list
    of maps/dicts, with title, description,
    and spotify ID.
    
    The user edits this file to remove the 
    playlists they don't want.
    """
    def __init__(self, token, username):
        """
        - create an API instance
        - populate the list of all playlists
        - dump it to a file
        """
        self.username = username
        self.sp = spotipy.Spotify(auth=token)

        # this is the master list of 
        # playlist IDs only
        self.master_list = None

        # this stores the details of each playlist
        self.playlists = []

        self.IDS_JSON_FILE = 'master_list.json'
        self.DETAILS_JSON_FILE = 'master_list_details.json'
        self.OUTPUT_DIR = 'output'
        self.ASSETS_DIR = 'assets'



    #############################
    # Function to make a static site
    # using the info obtained from
    # the Spotify API and the playlists
    # the user has selected.

    def static_site(self, overwrite=False):
        """
        Create all the pages
        """
        json_file = self.DETAILS_JSON_FILE
        output_dir = self.OUTPUT_DIR

        # populate self.playlists
        logging.debug('importing playlist details')
        self.import_playlist_details()

        if os.path.exists(output_dir) and overwrite is False:
            raise Exception("Error: output dir %s already exists!"%(output_dir))

        # Jinja env
        env = Environment(
                loader=PackageLoader('spots', 'templates'),
                autoescape=select_autoescape(['html', 'xml'])
        )

        self._copy_assets(env,overwrite)

        self._static_master_list(env)

        self._static_playlist_pages(env)


    def _copy_assets(self,env,overwrite=False):
        """
        Copy static assets into the output dir
        """
        output_dir = self.OUTPUT_DIR
        assets_dir = self.ASSETS_DIR

        if os.path.exists(self.OUTPUT_DIR) and overwrite is True:
            subprocess.call(['rm','-fr',self.OUTPUT_DIR])
            subprocess.call(['mkdir',self.OUTPUT_DIR])

        assets_source = glob.glob('%s/*'%(self.ASSETS_DIR))
        assets_target = '%s/.'%(self.OUTPUT_DIR)
        subprocess.call(['cp','-r',*assets_source,assets_target])

    def _static_master_list(self,env):
        """
        Render a static page for the master playlist.
        """
        output_dir = self.OUTPUT_DIR
        t = 'playlists.html'
        contents = env.get_template(t).render(
                playlists_items = self.playlists
        )
        with open('%s/index.html'%(output_dir),'w') as f:
            f.write(contents)

    def _static_playlist_pages(self,env):
        """
        Render a static page for each playlist.
        """
        output_dir = self.OUTPUT_DIR
        t = 'playlist.html'
        for playlist in self.playlists:
            contents = env.get_template(t).render(
                    playlist = playlist
            )
            with open('%s/%s.html'%(output_dir,playlist['id']),'w') as f:
                f.write(contents)



    #############################
    # Functions to import/export
    # a list of playlist IDs
    # easily edited by the user
    # to control which playlists
    # are rendered on the final
    # static site.
    #
    # The export_ method is intended
    # to be called by the user to export
    # all their playlists, and edit that
    # file.
    # 
    # The import_ method is not called by
    # the user directly, it is called by
    # other methods (below).

    def export_ids_list_to_file(self):
        """
        Step 1 by the user - dump the full list
        of Spotify playlists owned by the user 
        into a JSON file, and let the user edit
        this file to pick playlists.
        """
        json_file = self.IDS_JSON_FILE

        if os.path.exists(json_file):
            raise Exception('Error: %s already exists.'%(json_file))

        # Takes a while
        logging.debug('running method to load my playlists')
        my_playlists = self._get_my_playlists()
        logging.debug('done loading my playlists')

        logging.debug('dumping playlist ids to json file %s'%(json_file))
        with open(json_file,'w') as f:
            json.dump(my_playlists,f,indent=4)
        logging.debug('done dumping playlist ids to json file %s'%(json_file))


    def _get_my_playlists(self):
        """
        Private method: call the Spotify API to get
        a list of all playlists created by this user.
        """
        temp_playlists = []

        # Step 1:
        # Get every playlist a user follows

        logging.debug('getting every playlist from user %s'%(self.username))

        # Fencepost
        step = 50

        ############
        # Throttle API calls here
        ############

        logging.debug('first 50 api call')
        response = self.sp.user_playlists(
                self.username,
                limit=step,
                offset=0
        )
        temp_playlists += response['items']
        c = step

        total = response['total']

        while c < total:
            logging.debug('next %d api call'%(c))
            response = self.sp.user_playlists(
                    self.username,
                    limit=step,
                    offset=c
            )
            temp_playlists += response['items']
            c += step

        logging.debug('finished with api calls to get all playlists') 

        # Step 2:
        # Reduce list to playlists the user created

        logging.debug('reducing playlists to those created by this user')

        my_playlists = []
        logging.debug('About to process %d playlists'%(len(temp_playlists)))
        for i, playlist in enumerate(temp_playlists):

            pwner = playlist['owner']['id']

            if pwner == self.username:
                
                # ID for this playlist
                pid = playlist['id']

                # Name for this playlist
                pname = playlist['name']

                logging.debug('Processing playlist %s (%s)'%(pid,pname))

                results = self.sp.user_playlist(
                        self.username,
                        pid,
                        fields="description"
                )

                # Playlist description
                if 'description' in results.keys() and results['description'] is not None:
                    pdescr = HTMLParser().unescape(results['description'])
                else:
                    pdescr = ""

                # Populate the item we are saving
                save = dict(
                        spotify_id = pid,
                        name = pname,
                        description = pdescr
                )

                # Save details
                my_playlists.append(save)

        logging.debug('Reduced all %d playlists to %d owned by user'%(len(temp_playlists), len(my_playlists)))

        return my_playlists


    def import_ids_list_from_file(self):
        """
        Step 2 by the user - once the user has 
        edited the list of playlists, load the
        final list of Spotify playlist IDs to
        render on the static site.
        """
        json_file = self.IDS_JSON_FILE

        if not os.path.exists(json_file):
            raise Exception('Error: %s does not exist.'%(json_file))

        my_playlists = []

        logging.debug('opening json file %s'%(json_file))
        with open(json_file,'r') as f:
            my_playlists = json.load(f)
        logging.debug('done opening json file %s'%(json_file))

        playlist_ids = [j['spotify_id'] for j in my_playlists]

        self.master_list = playlist_ids

        logging.debug('master list has %d playlists'%(len(self.master_list)))



    #############################
    # Functions to get details about
    # each playlist in the master list
    # by calling the Spotify API or
    # using cached details.
    # 
    # The user will not call export_ or
    # import_ methods for playlist details.
    # 
    # The user will ask to create the static 
    # site, which will create the master list
    # and individual playlists.
    # 
    # Those methods will call these methods.

    def export_playlist_details(self):
        """
        Load the list of playlist IDs,
        look up the details of each playlist
        using the API, and store the details
        in a cache file.
        """
        json_file = self.DETAILS_JSON_FILE

        if os.path.exists(json_file):
            raise Exception('Error: %s already exists.'%(json_file))

        # Load the list of playlist ids,
        # then create the details file
        # by making API calls
        logging.debug('assembling the master list of playlist IDs')
        if self.master_list is None:
            # If the user hasn't done this yet,
            # this will fail
            self.import_ids_list_from_file()

        self.playlists = []

        # For each playlist id:
        for i, pid in enumerate(self.master_list):
            
            logging.debug('now processing playlist %d of %d'%(i+1, len(self.master_list)))

            # Get the playlist details
            logging.debug('calling api for playlist details...')
            deets = self.sp.user_playlist(
                    self.username,
                    pid,
                    fields="id,name,tracks,images,description,external_urls"
            )

            logging.debug('extracting playlist details...')
            self.playlists.append(self._extract_details(deets))

            logging.debug('done processing playlist %d of %d'%(i+1, len(self.master_list)))

            ## If you want to shorten this process,
            ## for example for testing,
            ## add a break statement here.
            #if (i+1)%10==0:
            #    break

        # Store details in the details json file
        with open(json_file,'w') as f:
            json.dump(self.playlists,f)

        logging.debug('done exporting playlist details to file')


    def _extract_details(self,playlist_json):
        """
        Keys:
        - name 
        - descr
        - images
        - external_urls
        - tracks
        """
        # Extract everything we will need
        # to make both the master list
        # and each individual list.
        # 
        # Do this by flattening maps/dicts
        # as much as possible.

        list_details = {}

        # spotify id
        list_details['id']    = playlist_json['id']
        list_details['name']  = playlist_json['name']
        list_details['url']   = playlist_json['external_urls']['spotify']

        # image
        if playlist_json['images'] is not None:
            list_details['image'] = playlist_json['images'][0]['url']
        else:
            list_details['image'] = "http://placehold.it/500x400"

        # description
        if 'description' in playlist_json.keys() and playlist_json['description'] is not None:
            list_details['description'] = HTMLParser().unescape(playlist_json['description'])
        else:
            list_details['description'] = ''

        # We also need to flatten maps/dicts
        # for individual tracks on this playlist
        # to make it easier to construct the 
        # individual playlist pages.

        # Iterate over items and flatten them
        playlist_items = []
        for p in playlist_json['tracks']['items']:
            it = {}
            it['name'] = p['track']['name']
            it['artist'] = ", ".join([j['name'] for j in p['track']['artists']])
            it['url_listen'] = p['track']['preview_url']
            it['url_spotify'] = p['track']['external_urls']['spotify']
            playlist_items.append(it)

        list_details['items'] = playlist_items

        list_details['total'] = playlist_json['tracks']['total']

        return list_details


    def import_playlist_details(self):
        """
        Import the playlist details from 
        the details JSON file.
        """
        json_file = self.DETAILS_JSON_FILE

        if os.path.exists(json_file):
            logging.debug('found json file %s, importing'%(json_file))
            # Details are stored in the details json file
            try:
                with open(json_file,'w') as f:
                    self.playlists = json.load(f)
                logging.debug('successfully loaded json file %s'%(json_file))
            except io.UnsupportedOperation:
                logging.debug('could not load json file %s'%(json_file))
                subprocess.call(['rm',json_file])
                logging.debug('empty json file %s, calling export playlist details'%(json_file))
                self.export_playlist_details()
        else:
            logging.debug('no json file %s, calling export playlist details'%(json_file))
            self.export_playlist_details()

