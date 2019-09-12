In this folder, we have some scripts to manage music and audio under linux.

all scripts use the config.yml.

# Mixxx Library Manager:
`manage-lirary.py`

This script helps you managing the mixxx library.
 
 - it checks if in your music folder are songs that are not (longer) in the mixxx library. These songs will be moved to a trash folder
 - it then checks for duplicates (based on the folder pattern, you told the script you want to use. if we have a file name conflict, it is handled as a duplicate)
 - now it helps you to resolve the duplicates. If multiple files are considered to be the same song, it asks you, which one to keep and which one you want to hide from mixxx. 
 - Next, we move the files to the target folders
 - Finally, we delete all empty folders
 - the last step is exporting every crate (and later also playlists) as m3u files.


# Rhythmbox Playlist Export
This script exports all Rhythmbox playlists as m3u files.

# Koel Library Sync.
This script clears the koel-database and adds all songs, that are in any of the m3u playlists to koel.

# Jack Start and Stop Scripts
These scripts can be placed in the autostart to start and stop the jack server.
