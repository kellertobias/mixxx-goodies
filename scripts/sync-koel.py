#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sqlite3

import sys
import os
from pprint import pprint

import yaml

# dbfile = os.path.expanduser('.koel.sqlite')
# conn = sqlite3.connect(dbfile)


with open("config.yml", 'r') as stream:
   try:
      config = yaml.safe_load(stream)
   except yaml.YAMLError as exc:
      print(exc)

library_location = os.path.expanduser(config["Library Base Path"])
playlist_basedir = os.path.expanduser(config["Playlist Exports"]["Base Directory"])

song_map = {}

for subdir, dirs, files in os.walk(playlist_basedir):
      for file in files:
         if not file.endswith('m3u'):
            continue

         with open(os.path.join(subdir, file), 'r') as m3u:
            for line in m3u:
               if line.startswith('#'):
                  continue
               songPath = os.path.abspath(os.path.join(playlist_basedir, line))
               print(songPath)

               songId = song_map.get(songPath, False)
               if not songId:
                  pass
                  # Find song in Database by its path
                  # songId = mysql.execute(...)
               
               # create entry in playlist for this song ID
