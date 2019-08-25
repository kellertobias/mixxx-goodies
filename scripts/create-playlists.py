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
