#!/usr/bin/env python3
#
# This Script Exports Playlists from rhythmbox
# in the same directory as we have configured the mixxx playlists to be exported to.
# this is helpful, if you want to copy the playlists to your phone.
# 

import os
from xml.dom import minidom
from xml.etree.ElementTree import tostring
import shutil

import datetime;
import yaml
from pprint import pprint

with open("config.yml", 'r') as stream:
   try:
      config = yaml.safe_load(stream)
   except yaml.YAMLError as exc:
      print(exc)

# Search for m3u files
# Read m3u Files
# for line im m3u file
#     check if music file exists
#     create folder structure
#     link file
#     if file does not exist, ignore line (remove from target m3u)

rhythmboxPath = os.path.expanduser('~/.local/share/rhythmbox/')

playlist_basedir = os.path.expanduser(config["Playlist Exports"]["Base Directory"])



rhPlaylistsXML = minidom.parse(rhythmboxPath + 'playlists.xml')
rhLibraryXML = minidom.parse(rhythmboxPath + 'rhythmdb.xml')
rhRelevantEntries = rhLibraryXML.getElementsByTagName('entry')

def getParent(et):
   return et.parentNode

fileList = set()

if not os.path.isdir(playlist_basedir):
   os.makedirs(playlist_basedir)

def create_playlist(playlistName, songs):
   """Make song Filename fitting to the database structure

   this ensures that duplicate songs don't clutter mp3 players'
   album views"""
   # rhLibraryXML.toprettyxml()
   # 
   print("Creating Playlist {}".format(playlistName))
   track_ids = []
   missing_tracks = []
   playlistFileName = "Music - %s.m3u" % (playlistName)
   print("Exporting: %s" % playlistFileName)
   with open(os.path.join(playlist_basedir, playlistFileName), "w") as m3u:
      m3u.write("#EXTM3U\n")

      for song in songs:
         # print(song.toprettyxml())
         location = song.getElementsByTagName('location')[0].firstChild.data
         if location.startswith('file://'):
            location = location[len('file://'):]
         location = os.path.relpath(location, playlist_basedir)
         print(location)

         m3u.write("#EXTINF:%s,%s - %s\n%s\n" % (
            int(song.getElementsByTagName('duration')[0].firstChild.data),
            song.getElementsByTagName('artist')[0].firstChild.data,
            song.getElementsByTagName('title')[0].firstChild.data,
            location
         ))






def export_playlist_static(playlist):
   i = 0

   fileLocations = [file.firstChild.data for file in playlist.getElementsByTagName('location')]
   currentEntries = [elm for elm in rhRelevantEntries if elm.getElementsByTagName('location')[0].firstChild.data in fileLocations]
   create_playlist(playlist.attributes["name"].value, currentEntries)
   return i


def export_playlist_automatic(playlist):
   search = ''
   ts = datetime.datetime.now().timestamp()
   rules = playlist.getElementsByTagName('conjunction')[0]
   rules = rules.getElementsByTagName('subquery')[0]
   rules = rules.getElementsByTagName('conjunction')[0]

   for rule in rules.childNodes:
      if not rule.localName:
         continue

      comparator = rule.localName
      prop = rule.attributes['prop'].value
      value = rule.firstChild.data
      try:
         valueInt = int(float(("" + value).replace(',', '.')))
      except:
         valueInt = 0

      if prop == 'genre-folded':
         prop = 'genre'

      def compare(elm):
         songValue = elm.firstChild.nodeValue
         if comparator == 'current-time-within':
            return int(float(songValue.replace(',', '.'))) >= (ts - valueInt)

         if comparator == 'greater':
            return int(float(songValue.replace(',', '.'))) >= valueInt

         if comparator == 'less':
            return int(float(songValue.replace(',', '.'))) <= valueInt

         if comparator == 'equals':
            return int(float(songValue.replace(',', '.'))) == valueInt

         if comparator == 'like':
            return value in songValue

         if comparator == 'not-like':
            return value not in songValue

      relevantEntries = rhRelevantEntries
      currentEntries = rhLibraryXML.getElementsByTagName(prop)
      relevantEntries = [elm.parentNode for elm in currentEntries if elm.parentNode.attributes["type"].value == 'song' and compare(elm) and elm.parentNode in relevantEntries]

   if len(relevantEntries) < 1:
      print("\n=== No Results ===\n")
      return 0

   print("")
   i = 0
   create_playlist(playlist.attributes["name"].value, relevantEntries)
   
   return i
   

rhPlaylists = rhPlaylistsXML.getElementsByTagName('playlist')

# for the_file in os.listdir(playlist_basedir):
#     file_path = os.path.join(playlist_basedir, the_file)
#     try:
#         if os.path.isfile(file_path):
#             os.unlink(file_path)
#         elif os.path.isdir(file_path): shutil.rmtree(file_path)
#     except Exception as e:
#         print(e)


for playlist in rhPlaylists:
   name = playlist.attributes["name"].value
   if playlist.attributes["type"].value not in ['static', 'automatic']:
      continue

   if name in ['Zuletzt hinzugefügt', 'Recently Added']:
      continue

   print("Exporting {}".format(name))
   print("===================================================")
   i = 0

   if playlist.attributes["type"].value == 'static':
      i = export_playlist_static(playlist)

   elif playlist.attributes["type"].value == 'automatic':
      i = export_playlist_automatic(playlist)
   print("---------------------------------------------------")
   print("Exported {} Songs".format(i))
   print("")


exit()
