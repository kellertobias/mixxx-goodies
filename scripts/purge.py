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


dbfile = os.path.expanduser('~/.mixxx/mixxxdb.sqlite')
conn = sqlite3.connect(dbfile)


with open("config.yml", 'r') as stream:
   try:
      config = yaml.safe_load(stream)
   except yaml.YAMLError as exc:
      print(exc)


for (trackId, location, locationId) in conn.execute('''
   SELECT 
      library.id as id, track_locations.location as location,
      track_locations.id as locationId
   FROM library
   LEFT JOIN track_locations ON(library.location = track_locations.id)
   WHERE mixxx_deleted == 1
'''):
   try:
      print(location)
      os.remove(location)
   except FileNotFoundError as e:
      print("!!!!!!!! COULD NOT FIND FILE !!!!!!!!!!!!")
      print(source)
      sleep(2)
   except Exception as e:
      print(e)
      raise e

   conn.execute('''
      DELETE FROM track_locations WHERE id = ?
   ''', (locationId, ))
   conn.commit()

   conn.execute('''
      DELETE FROM cues WHERE track_id = ?
   ''', (trackId, ))
   conn.commit()

   conn.execute('''
      DELETE FROM track_analysis WHERE track_id = ?
   ''', (trackId, ))
   conn.commit()

   conn.execute('''
      DELETE FROM crate_tracks WHERE track_id = ?
   ''', (trackId, ))
   conn.commit()

   conn.execute('''
      DELETE FROM PlaylistTracks WHERE track_id = ?
   ''', (trackId, ))
   conn.commit()

   conn.execute('''
      DELETE FROM library WHERE id = ?
   ''', (trackId, ))
   conn.commit()
