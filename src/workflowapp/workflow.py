#!/usr/bin/env python
# coding=utf-8
"""Workflow tool application"""

import os
import logging
import json
import csv
import requests
from requests.exceptions import ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


MODULE_FILE_PATH = os.path.realpath(__file__)
head, tail = os.path.split(MODULE_FILE_PATH)
pathsplit = head.split("/")
del pathsplit[len(pathsplit) - 1]
del pathsplit[len(pathsplit) - 1]
APP_DIR_PATH = "/".join(pathsplit)
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.1


def logger_config():
    logging.basicConfig(level=logging.INFO, format=("[###%(levelname)s] "
                                                    "%(asctime)s: "
                                                    "%(filename)s: "
                                                    "%(funcName)s(): "
                                                    "%(lineno)d: "
                                                    "%(message)s"))
    logging.info("Started")


def load_settings(filepath):
    if filepath is None:
        raise TypeError

    if not os.path.isfile(filepath):
        logging.error("The file does not exist, %s", filepath)
        raise IOError

    logging.info("Loading configuation settings from %s", filepath)
    settings = dict()
    try:
        with open(filepath, "r") as f:
            settings = json.load(f)
        return settings
    except IOError as io:
        logging.error("An error has occ®urred with reading file, %s", io)


def _output_to_json_file(output_filename, textfile):
    if output_filename is None or textfile is None:
        raise TypeError

    logging.info("Reading file into the json file %s", output_filename)
    try:
        with open(output_filename, "w") as outfile:
            reader = csv.DictReader(textfile.splitlines(),
                                    delimiter='\t')
            json.dump(list(reader), outfile, ensure_ascii=False,
                      sort_keys=True, indent=4)
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def get_inventory(url, jsonfile):
    if url is None or jsonfile is None:
        raise TypeError

    logging.info("Retrieve http request payload from %s", url)
    try:
        session = requests.Session()
        session_retries = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=session_retries))
        response = session.get(url)
        return response.text
    except ValueError as ve:
        logging.error("An error with requesting api, %s", ve)
    except requests.exceptions.HTTPError as he:
        logging.error("An httperror has occurred, %s", he)
    except ConnectionError as ce:
        logging.error("Max number of network retries, %s", ce)
        logging.error("Exiting the program")
        exit(1)


def process_inventory(filepath):
    if filepath is None:
        raise TypeError

    if not os.path.isfile(filepath):
        logging.error("The file does not exist, %s", io)
        raise IOError

    logging.info("Loading %s", filepath)
    try:
        with open(filepath, "r") as jsonfile:
            inventory = json.load(jsonfile)
        return inventory
    except IOError as io:
        logging.error("An error has occurred with loading file, %s", io)


def run_statistics_on_column(inventory, column_name, jsonfile):
    if inventory is None or column_name is None or jsonfile is None:
        raise TypeError

    logging.info("Run stats against column %s from the file %s",
                 column_name, jsonfile)
    values = list()

    def _median(sorted_values):
        if sorted_values is None:
            raise TypeError
        result = 0.0
        size = len(sorted_values)
        is_even = (size % 2 == 0)
        if is_even:
            hi = float(sorted_values[size / 2])
            lo = float(sorted_values[(size / 2) - 1])
            result = (hi + lo) / 2
        else:
            result = float(sorted_values[size / 2])
        return result

    def _max(sorted_values):
        if sorted_values is None:
            raise TypeError
        return float(sorted_values[0])

    def _min(sorted_values):
        if sorted_values is None:
            raise TypeError
        return float(sorted_values[len(sorted_values) - 1])

    for row_dict in inventory:
        if row_dict is None:
            raise TypeError
        values.append(row_dict.get(column_name))

    sorted_values = sorted(values, key=float, reverse=True)
    values_dict = dict([("Maximum", _max(sorted_values)),
                        ("Minimum", _min(sorted_values)),
                        ("Median", _median(sorted_values))])

    try:
        with open(jsonfile, "w") as outfile:
            json.dump(values_dict, outfile)
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def print_filesize(directory):
    if directory is None:
        raise TypeError

    if not os.path.isdir(directory):
        logging.error("The directory does not exist, %s", directory)
        raise IOError

    try:
        files = os.listdir(directory)
        for a_file in files:
            print "\nfile: " + a_file
            print "size: " + str(os.path.getsize(directory + a_file))
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def run():
    logger_config()
    DEFAULT_CONFIG_PATH = APP_DIR_PATH + "/config/workflows.json"
    settings = load_settings(DEFAULT_CONFIG_PATH)

    try:
        DEFAULT_WORKFLOW = settings[0].get("operations")
        OUTPUT_DIR = APP_DIR_PATH + "/output/"
        INV_FILENAME = DEFAULT_WORKFLOW[0].get("filename")
        INVENTORY_URL = DEFAULT_WORKFLOW[0].get("input")
        INV_JSON_FILE = DEFAULT_WORKFLOW[1].get("filename")
        RUN_STATS_ON_COLUMN_NAME = (DEFAULT_WORKFLOW[2].get("extra")[0]
                                    .get("column_name"))
        STATS_JSON_FILE = DEFAULT_WORKFLOW[2].get("filename")

        response_text = get_inventory(INVENTORY_URL + INV_FILENAME,
                                      OUTPUT_DIR + INV_JSON_FILE)
        _output_to_json_file(OUTPUT_DIR + INV_JSON_FILE, response_text)
        inventory = process_inventory(OUTPUT_DIR + INV_JSON_FILE)
        run_statistics_on_column(inventory, RUN_STATS_ON_COLUMN_NAME,
                                 OUTPUT_DIR + STATS_JSON_FILE)
        print_filesize(OUTPUT_DIR)
    except ValueError as e:
        logging.error("An error has occurred, %s", e)
    except TypeError as te:
        logging.error("An error has occurred, %s", te)

if __name__ == "__main__":
    run()
