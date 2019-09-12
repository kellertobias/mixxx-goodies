#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import sqlite3

from shutil import copy

import shutil
import json

import codecs

import sys
import os
from pprint import pprint

import yaml
from datetime import datetime
from textwrap import wrap
from termcolor import colored
from time import sleep

from slugify import slugify
from terminaltables import AsciiTable, DoubleTable, SingleTable

import sys

def query_yes_no(question, options=[('y', True, True), ('n', False, False)]):
   """Ask a yes/no question via raw_input() and return their answer.

   "question" is a string that is presented to the user.
   "default" is the presumed answer if the user just hits <Enter>.
   It must be "yes" (the default), "no" or None (meaning
   an answer is required of the user).

   The "answer" return value is True for "yes" or False for "no".
   """
   valid = {}
   default = None
   prompt = []
   for (inp, outp, isDefault) in options:
      if isDefault:
         default = outp
         prompt.append(("%s" % inp).title())
      else:
         prompt.append("%s" % inp)
      valid[inp] = outp

   prompt = "[" + "/ ".join(prompt) + "] "

   while True:
      sys.stdout.write(question + prompt)
      choice = input().lower()

      if default is not None and choice == '':
         return default
      elif choice in valid:
         return valid[choice]
      else:
         sys.stdout.write("Please respond with one of the available options.\n")

dbfile = os.path.expanduser('~/.mixxx/mixxxdb.sqlite')
conn = sqlite3.connect(dbfile)


with open("config.yml", 'r') as stream:
   try:
      config = yaml.safe_load(stream)
   except yaml.YAMLError as exc:
      print(exc)

genre_mapping = {}
library_location = os.path.expanduser(config["Library Base Path"])
location_template = os.path.join(library_location, config["Target Path"])

location_template_parts = location_template.split('%')
tagOpen = False
location_template = []
for lpart in location_template_parts:
   location_template.append((lpart, tagOpen))
   tagOpen = not tagOpen

map_other = False
mapped_genre_prefixes = []


for target_folder in config['Genre To Folder']:
   if type(config['Genre To Folder'][target_folder]) is bool:
      map_other = target_folder
      continue

   for genre in config['Genre To Folder'][target_folder]:
      mapped_genre_prefixes.append(genre)
      genre_mapping[genre] = target_folder

mapped_genre_prefixes.sort(reverse=True)


def get_genre_mapping(genre):
   try:
      if genre is None:
         genre = "Unknown"
      genre_prefix = next(x for x in mapped_genre_prefixes if genre.startswith(x))
      return genre_mapping[genre_prefix]
   except StopIteration:
      if map_other is False:
         return False
      return map_other
   return False

not_mapped = []

degraded_ids = []

def disassemble_track(track):
   (id, artist, album, title, year, genre, comment, duration, bitrate, samplerate, added, rating, composer, grouping, location, directory, filesize, filename, locationId) = track
   
   datetime_added = datetime.strptime(added, '%Y-%m-%dT%H:%M:%S.%fZ')
   filename, file_extension = os.path.splitext(filename)

   file_extension = file_extension.strip('.')

   return {
      'id': id,
      'artist': artist,
      'album': album,
      'title': title,
      'year': year,
      'genre': genre,
      'mappedgenre': genre_mapping[genre],
      'location': location,
      'comment': comment,
      'duration': duration,
      'bitrate': bitrate,
      'samplerate': samplerate,
      'added': added,
      'datetime-added': datetime_added,
      'added-year': str(datetime_added.year),
      'added-month': str(datetime_added.month),
      'rating': rating,
      'composer': composer,
      'grouping': grouping,
      'directory': directory,
      'filesize': filesize,
      'filename': filename,
      'locationId': locationId,
      'ext': file_extension,
   }

def check_degraded(track):
   pass

replacements = ((x, config["Filename Replacements"][x]) for x in config["Filename Replacements"])
# for (a,b) in replacements:
#    print(a, '=', b)

def clean_variable(filename):
   """
   Normalizes string, converts to lowercase, removes non-alpha characters,
   and converts spaces to hyphens.
   """

   filename = slugify(
      filename,
      separator=" ",
      replacements=replacements
   )
   filename = filename.title()

   for (replaceSource, replacementTarget) in replacements:
      filename = filename.replace(replaceSource, replacementTarget)

   return filename


def build_track_location(track):
   track_location = ""
   for (part, isVariable) in location_template:
      if isVariable:
         key = part
         part = track.get(key, None)
         if part is None:
            part = 'Unknown ' + key
         if key not in ["mappedgenre", 'ext']:
            part = clean_variable(part)

      try:
         track_location += part
      except TypeError as e:
         print("Cannot Concat", key, part)
         raise e

   return track_location

   

# First we get all relevant genre Mappings and show genres that have no mapping.
# If we have genres that have no mappings, we abort with an error.
for (genre, ) in conn.execute('''
   SELECT genre FROM library GROUP BY genre
'''):
   genre_mapping[genre] = get_genre_mapping(genre)
   if not genre_mapping[genre]:
      not_mapped.append(genre)

print("======================================")
print("===  Checking for unmapped Genres  ===")
print("======================================")
if len(not_mapped) > 0:
   print("We have some unmapped genres:")
   for genre in not_mapped:
      print(" - %s" % genre)
   sys.exit(0)

print("       >>> Everything Fine. <<<")
print("======================================")


print("")
print("Will now check for unlinked tracks and move them to a Dumpster Folder.")
print("This may modify your filesystem.")

cont = query_yes_no("List files, not in mixx library?")

if cont:
   detached_files = []
   for subdir, dirs, files in os.walk(library_location):
      for file in files:
         filelocation = os.path.join(subdir, file)
         trackFound = False
         for track in conn.execute('''
            SELECT 
               id
            FROM track_locations
            WHERE location = ?
         ''', (filelocation, )):
            trackFound = True
         
         if not trackFound:
            print("NO Track Found", filelocation, os.path.basename(file))
            detached_files.append(filelocation)

   dumpster_directory = os.path.expanduser(config["Dumpster Directory"])
   now = datetime. now()

   dumpster_template = os.path.join(dumpster_directory, "%s-{index}-{orig}" % now. strftime("%Y-%m-%d-%H-%M"))

   print("Found %s detached files. Will move them to the dumpster-directory, prepended with the date and a acounter." % len(detached_files))
   cont = query_yes_no("Move files, not in mixx library to new dumpster?")

   if cont:
      i = 0
      for file in detached_files:
         print("Moving %s" % file)
         shutil.move(file, dumpster_template.format(
            index=i,
            orig=os.path.basename(file)
         ))


moved_tracks = []
locations = {}
duplicates = {}

print("======================================")
print("== Checking Tracks for moved Tracks ==")
print("======================================")
for track in conn.execute('''
   SELECT 
      library.id as id, artist, album,
      title, year, genre,
      comment,
      duration, bitrate, samplerate,
      datetime_added, rating,
      composer, grouping,
      track_locations.location as location,
      directory, filesize, filename, track_locations.id as locationId
   FROM library
   LEFT JOIN track_locations ON(library.location = track_locations.id)
   WHERE mixxx_deleted == 0
'''):
   track = disassemble_track(track)
   check_degraded(track)
   track_location = build_track_location(track)

   if track_location != track["location"]:
      moved_tracks.append((track["id"], track["locationId"], track["location"], track_location))

   if locations.get(track_location, False):
      locations[track_location].append(track)
      duplicates[track_location] = (track, locations[track_location])
   else:
      locations[track_location] = [track]


if len(duplicates) > 0:
   print("       !!!We have duplicates!!!")
   print("")
   print("Here's the duplicates")
   for track_location in duplicates:
      (track, otherTracks) = duplicates[track_location]
      print(' - [%s] %s - %s' % (track["genre"], track["artist"], track["title"]))
   print("")
   print(" > %s duplicates total" % len(duplicates))
   print("We cannot proceed when we have duplicates!")

   cont = query_yes_no("Do you want me help to resolve these duplicates?")
   if not cont:
      print("Ok, Please do it yourself and come back. Goodbye.")
      sys.exit(0)

   for track_location in duplicates:
      os.system('clear')
      (track, allSimilarTracks) = duplicates[track_location]

      col_ids = ["TrackID"]
      col_tracks = ["Select"]
      col_title = ["Title"]
      col_artist = ["Artist"]
      col_rating = ["Rating"]
      col_added = ["Added"]
      col_duration = ["Duration"]
      col_year = ["Year"]
      col_bitrate = ["Bitrate"]
      col_genre = ["Genre"]
      col_location = ["Path"]

      i = 1
      oldestIndex = False
      oldestDate = datetime.now()
      highestBitrate = 0
      highestRating = 0
      highestRatingIndex = False
      shortest = 1000000
      longest = 0 
      for track in allSimilarTracks:
         added = track.get('datetime-added', datetime.now())
         duration = int(track.get('duration', 0))
         if added <= oldestDate:
            oldestDate = added
            oldestIndex = i

         if duration > longest:
            longest = int(duration)

         if duration < shortest:
            shortest = int(duration)

         bitrate = track.get('bitrate', '--- ??? ---')
         if bitrate >= highestBitrate:
            highestBitrate = bitrate

         rating = track.get('rating', '--- ??? ---')
         if rating > highestRating or (highestRatingIndex is None and rating >= highestRating):
            highestRating = rating
            highestRatingIndex = i

         col_tracks.append(i)
         i += 1
         col_ids.append(track.get('id', '!!!'))
         col_title.append(track.get('title', '--- ??? ---'))
         col_artist.append(track.get('artist', '--- ??? ---'))
         col_rating.append(rating)
         col_duration.append(duration)
         col_added.append(track.get('added', '--- ??? ---'))
         col_year.append(track.get('year', '--- ??? ---'))
         col_genre.append(track.get('genre', '--- ??? ---'))
         col_bitrate.append(bitrate)
         col_location.append('')



      data = [
         col_tracks,
         col_ids,
         col_title,
         col_artist,
         col_rating,
         col_added,
         col_year,
         col_duration,
         col_genre,
         col_bitrate,
         col_location,
      ]
      table_instance = SingleTable(
         data,
         "Resolving Duplicate: %s - %s (%s)" % (track["artist"], track["title"], track["genre"]),
      )
      table_instance.inner_row_border = True
      table_instance.justify_columns[0] = 'right'

      for (row, col) in [
         (5, oldestIndex),
      ]:
         table_instance.table_data[row][col] = colored(table_instance.table_data[row][col], "white", "on_green")

      for i in range(len(allSimilarTracks)):
         rating = table_instance.table_data[4][i + 1]
         if i + 1 == highestRatingIndex:
            backcol = 'green'
         else:
            backcol = 'grey'
         rating = colored('★' * (rating), 'yellow') +colored('★' * (5-rating), backcol)
         table_instance.table_data[4][i + 1] = rating

         for (index, compare, color) in [
            (9, highestBitrate, 'on_green'),
            (7, longest, 'on_yellow'),
         ]:
            data = table_instance.table_data[index][i + 1]
            if data == compare:
               table_instance.table_data[index][i + 1] = colored(data, "white", color)


      i = 1
      table_width = 0
      columns, rows = shutil.get_terminal_size()
      max_width = int((columns - 40) / len(allSimilarTracks))

      for track in allSimilarTracks:
         location = track.get('location', '--- ??? ---')
         for match in config['Duplicate Highlight Locations']:
            color = config['Duplicate Highlight Locations'][match]
            location = location.replace(match, colored(match, 'white', "on_%s" % color))
         wrapped_string = '\n'.join(wrap(location, max_width))
         table_instance.table_data[10][i] = wrapped_string
         i += 1

      print("")
      print(table_instance.table)
      print("")

      options = [('Skip', False, True)]
      for i in range(len(allSimilarTracks)):
         options.append(('%s' % (i + 1), (i + 1), False))
      keepID = query_yes_no('Select Track to keep', options)
      if keepID:
         print("Keeping Track %s" % keepID)
         i = 1
         for track in allSimilarTracks:
            if i != keepID:
               print("Hiding Number", i, "TrackID:", track.get('id'), track.get('location'))
               cur = conn.cursor()
               cur.execute("""
                  UPDATE library
                  SET
                     mixxx_deleted = 1
                  WHERE
                     id = ?
               """, (track.get('id'), ))
               conn.commit()
               print(cur.rowcount)
            else:
               print("Updating Number", i, "TrackID:", track.get('id'), highestRating)

               cur = conn.cursor()
               cur.execute("""
                  UPDATE library
                  SET
                     mixxx_deleted = 0,
                     rating = ?
                  WHERE
                     id = ?
               """, (highestRating, track.get('id')))
               conn.commit()
            i += 1


   print("========================================")
   print("Please Restart this script now.")
   sys.exit(0)   
else:
   print(">>> Everything Fine. No Duplicates <<<")
   print("======================================")

if len(moved_tracks) > 0:
   print("")
   print("")
   print("")
   print("These files will be moved:")
   print("")

   for (trackId, trackLocationId, source, target) in moved_tracks:
      if source.startswith(library_location):
         source = source[len(library_location):]
      if target.startswith(library_location):
         target = target[len(library_location):]
      print(" > %s --> %s" % (source, target))

   print("Will now move %s tracks to their new location" % len(moved_tracks))
   print("This may modify your filesystem and mixxx library.")

   cont = query_yes_no("Move files to new location?")
else:
   print("No files to move")

   cont = query_yes_no("Continue to next step?")
   if not cont:
      sys.exit(0)

if cont:
   for (trackId, trackLocationId, source, target) in moved_tracks:
      directory = os.path.dirname(target)
      filename = os.path.basename(target)
      if not os.path.exists(directory):
         print(" > Creating Directory %s" % directory)
         os.makedirs(directory)

      try:
         print((target, filename, directory, trackLocationId, source))
         shutil.move(source, target)
         cur = conn.cursor()
         cur.execute("""
            UPDATE track_locations
            SET
               location = ?,
               filename = ?,
               directory = ?
            WHERE
               id = ? AND
               location = ?
         """, (target, filename, directory, trackLocationId, source))
         conn.commit()
      except FileNotFoundError as e:
         print("!!!!!!!! COULD NOT FIND FILE !!!!!!!!!!!!")
         print(source)
         sleep(2)
      except Exception as e:
         print(e)
         raise e

print("======================================")
print("Doing final cleanup (Removing empty folders)")

# Iterate over the directory tree and check if directory is empty.
for (dirpath, dirnames, filenames) in os.walk(library_location):
    if len(dirnames) == 0 and len(filenames) == 0 :
        shutil.rmtree(dirpath)

def build_playlists(playlist):
   print("Syncing Playlist %s" % playlist.get('name', "No Name"))



if config.get("Playlist Exports", False):
   create_playlists = config["Playlist Exports"].get('Autocreate Playlists', False)
   print("Playlist Autocreate (Not implemented at the moment)")
   for playlist in create_playlists:
      build_playlists(playlist)

   export_playlists = []
   playlist_basedir = os.path.expanduser(config["Playlist Exports"].get('Base Directory', False))

   common_prefix = os.path.commonpath([playlist_basedir, library_location])


   for (crateId, name) in conn.execute('''
      SELECT 
         id,
         name
      FROM crates
      WHERE show == 1
   '''):
      print("Playlist: %s" % name)
      playlist_entry = []
      for (trackId, location, title, artist, duration) in conn.execute('''
         SELECT 
            library.id as trackId,
            track_locations.location as location,
            library.title as title,
            library.artist as artist,
            library.duration as duration
         FROM crate_tracks
         LEFT JOIN library ON(crate_tracks.track_id = library.id)
         LEFT JOIN track_locations ON(library.location = track_locations.id)
         WHERE crate_tracks.crate_id == ?
      ''', (crateId, )):
         playlist_entry.append((title, artist, duration, location))

      export_playlists.append((name, "Crate", playlist_entry))

   for (playlistName, playlistType, tracks) in export_playlists:
      playlistFileName = "%s - %s.m3u" % (playlistType, playlistName)
      print("Exporting: %s" % playlistFileName)
      with open(os.path.join(playlist_basedir, playlistFileName), "w") as m3u:
         m3u.write("#EXTM3U\n")

         for (title, artist, duration, location) in tracks:
            location = os.path.relpath(location, playlist_basedir)
            m3u.write("#EXTINF:%s,%s - %s\n%s\n" % (int(duration), artist, title, location))
