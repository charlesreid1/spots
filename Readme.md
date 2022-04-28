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
each of the user's playlists.

The next step will use the data in `master_list.json` to generate
a static site containing a list of all the Spotify playlists in
`master_list.json`.

Before running that step, `master_list.json` can/should be edited
to filter any playlists that should be excluded from the final
static site.

### Workflow

We typically store the original `master_list.json` and an edited
`master_list_edited.json` in a folder named `master_list_YYYY-MM`.

The `master_list_edited.json` is edited by hand to contain only
the playlists to end up on the final page.

`mster_list_YYYY-MM/master_list_edited.json` is then copied BACK
to `master_list.json` in the repo root directory, before the next
step, the `create` action, is run.

### What if no editing is necessary?

If no editing of the list of playslists is necessary, then the
`master_list.json` file can be used as generated in Step 1.

### Checking `master_list.json`

Make sure and lint the JSON file before running Step 3. This can be
done with Python:

```
$ python -m json.tool master_list.json
```

## Step 3: Create Static Site

Create a static site using the spotify playlist IDs specified by the user
by calling `spots` with the `create` action:

```
python spots.py [username] create
```

This will generate the site into the directory specified by `OUTPUT_DIR` in `spots_objects.py`.

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
