# spots

this repo contains scripts to use the spotify API
to extract information about playlists and construct
a static site with HTML versions of each playlist,
its tracks, album art, descriptions, spotify links,
etc.

The script uses OAuth, and requires each user to log in
via a web browser to authorize access to their playlists.

## Step 1: Extract Playlist Data

The first step is to extract a list of all playlists, 
playlist art, and descriptions, to compile and let the
user select which playlists they are interested in.

Use the API to extract this information.

Export to a file (just a list of playlist IDs?).

## Step 2: Create Static Site

Create a static site using the spotify playlist IDs specified by the user.

Read a list of playlist IDs from a file


