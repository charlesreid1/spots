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

To run the extract step with a spotify username:

```
python spots.py [username] extract
```

## Step 2: Edit Playlist Data

The prior step will output a `master_list.json` containing info about
each of the user's playlists. This JSON list can be edited to remove
any playlists that should not be included in the static site.

## Step 3: Create Static Site

Create a static site using the spotify playlist IDs specified by the user:

```
python spots.py [username] create
```
