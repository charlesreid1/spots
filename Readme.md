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

This should initiate a manual authentication step by opening
a web browser where you can log into Spotify with your username
and password, as part of three-legged authentication.

If the authetication step with Spotify is successful, you will
see `spots` begin to process all of your playlists to compile them
into JSON files.

If the authetication step with Spotify fails, see below.

### Step 1B: Clear The Cache

If the above step results in an invalid (old) token, remove the file `.cache-<username>`.

## Step 2: Edit Playlist Data

Step 1 will result in a `master_list.json` containing info about
each of the user's playlists. This JSON list can be modified by hand
to remove any playlists to be excluded from the final site.

## Step 3: Create Static Site

Create a static site using the spotify playlist IDs specified by the user
by calling `spots` with the `create` action:

```
python spots.py [username] create
```

## Deploy Strategy

Clone a copy of the repo (the `gh-pages` branch) in the current directory into the
directory `site`:

```
git clone -b gh-pages git@github.com:charlesreid1/spots site
```

Have the `spots.py` script generate the static contents of the site in the `output` directory.
This is the default output directory (see `OUTPUT_DIR` in `spots_objects.py`), so you shouldn't
have to do anything to get this step to work.

Manual check: Once you have run the create action, cehck the contents of the `output` directory
manually to ensure it is okay.

If everything is okay, clear out the `site` folder, and copy the contents of `output` into `site`:

```
rm -fr site/*
cp -r output/* site/.
```

When that is finished, commit all changes to the `gh-pages` branch by committing the
new contents of the `site` directory, probably something like this:

```
cd site
git add -A .
git commit -a -m 'update gh-pages branch'
git push origin gh-pages
```
