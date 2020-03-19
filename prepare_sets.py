# -*- coding: utf-8 -*-

import argparse
import math
import os
from pprint import pprint
import sys

import lib.io_utils as io
import lib.list_utils as lu

# input
parser = argparse.ArgumentParser()
parser.add_argument("-config", dest="CONFIG_FILE", default="config-sample.json", help="Config file")
a = parser.parse_args()

config = io.readJSON(a.CONFIG_FILE)
configSets = config["sets"]

INPUT_FILE = config["metadata"]["src"]
ID_COLUMN = config["metadata"]["id"]
OUTPUT_DIR = "apps/{appname}/".format(appname=config["name"])
OUTPUT_SET_DIR = OUTPUT_DIR + "data/sets/"
CONFIG_FILE = OUTPUT_DIR + "js/config/config.sets.js"

# Make sure output dirs exist
io.makeDirectories([OUTPUT_SET_DIR, CONFIG_FILE])
fieldnames, items = io.readCsv(INPUT_FILE, parseNumbers=False)

# Sort so that index corresponds to ID
items = sorted(items, key=lambda item: item[ID_COLUMN])
items = lu.addIndices(items)

jsonsets = {}
for keyName, options in configSets.items():
    setItems = lu.filterByQueryString(items, options["query"])
    if len(setItems) > 0:
        print("%s results found for '%s'" % (len(setItems), options["query"]))
    else:
        print("Warning: '%s' produces no results" % options["query"])
        continue

    # limit the results if specified
    if "limit" in options and len(setItems) > options["limit"]:
        setItems = setItems[:options["limit"]]

    # Write set file
    setOutFile = OUTPUT_SET_DIR + keyName + ".json"
    outjson = [item["index"] for item in setItems]
    io.writeJSON(setOutFile, outjson)
    jsonsets[keyName] = {"src": setOutFile}

# Write config file
outjson = {
    "sets": jsonsets
}
io.writeJSON(CONFIG_FILE, outjson, pretty=True, prepend="_.extend(CONFIG, ", append=");")
