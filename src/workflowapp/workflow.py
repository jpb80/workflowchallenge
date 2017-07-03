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
                                                    "%(message)s\n"))


def setup(filepath, outputpath):
    if filepath is None or outputpath is None:
        logging.error("The filepath, outputpath cannot be None")
        raise TypeError("The paths cannot be None")

    _setup_output_dir(outputpath)

    if not os.path.isfile(filepath):
        logging.error("The file does not exist, %s", filepath)
        raise IOError("The filepath is not a file")

    logging.info("Loading configuation settings from %s", filepath)
    settings = dict()
    try:
        with open(filepath, "r") as f:
            settings = json.load(f)
        return settings
    except IOError as io:
        logging.error("An error has occurred with reading file, %s", io)


def _setup_output_dir(outputpath):
    try:
        if not os.path.isdir(outputpath):
            os.mkdir(outputpath)
    except OSError as ose:
        logging.error("An error with creating output dir, %s", ose)
        exit(1)


def _output_to_json_file(output_filename, textfile):
    STEP = "Workflow Step #1"
    logging.info("%s: Export file to JSON.", STEP)
    if output_filename is None or textfile is None:
        logging.error("%s: The output_filename or textfile does not exist",
                      STEP)
        raise TypeError("output_filename, textfile cannot be None")

    logging.info("Reading file into the json file %s", output_filename)
    try:
        with open(output_filename, "w") as outfile:
            reader = csv.DictReader(textfile.splitlines(),
                                    delimiter='\t')
            json.dump(list(reader), outfile, ensure_ascii=False,
                      sort_keys=True, indent=4)
    except IOError as io:
        logging.error("%s: An error has occurred with writing file, %s",
                      STEP, io)


def get_inventory(url, jsonfile):
    STEP = "Workflow Step #1"
    logging.info("%s: Retrieve file from url.", STEP)

    if url is None or jsonfile is None:
        logging.error("%s: The url or jsonfile does not exist", STEP)
        raise TypeError("url, jsonfile cannot be None")

    logging.info("Retrieve http request payload from %s", url)
    try:
        session = requests.Session()
        session_retries = Retry(
            total=MAX_RETRIES,
            backoff_factor=BACKOFF_FACTOR,
            status_forcelist=[500, 502, 503, 504, 404, 403, 401])
        session.mount('http://', HTTPAdapter(max_retries=session_retries))
        response = session.get(url)
        return response.text
    except ValueError as ve:
        logging.error("%s: An error with requesting api, %s", STEP, ve)
    except requests.exceptions.HTTPError as he:
        logging.error("%s: An httperror has occurred, %s", STEP, he)
    except ConnectionError as ce:
        logging.error("%s: Max number of network retries, %s", STEP, ce)
        logging.error("Exiting the program")
        exit(1)


def process_inventory(filepath):
    STEP = "Workflow Step #2"
    logging.info("%s: Load the inventory JSON file.", STEP)

    if filepath is None:
        logging.error("%s: The filepath does not exit", STEP)
        raise TypeError("filepath cannot be None")

    if not os.path.isfile(filepath):
        logging.error("%s: The file does not exist, %s", STEP, filepath)
        raise IOError("filepath is not a file")

    logging.info("Loading %s", filepath)
    try:
        with open(filepath, "r") as jsonfile:
            inventory = json.load(jsonfile)
        return inventory
    except IOError as io:
        logging.error("%s: An error has occurred with loading file, %s",
                      STEP, io)


def run_statistics_on_column(inventory, column_name, jsonfile):
    STEP = "Workflow Step #3"
    logging.info("%s: Getting the maximum, minimum, and median of dataset.",
                 STEP)

    if inventory is None or column_name is None or jsonfile is None:
        logging.error("%s: inventory, column_name, jsonfile cannot be None",
                      STEP)
        raise TypeError("inventory, column_name, or jsonfile cannot be None")

    values = list()
    for row_dict in inventory:
        if row_dict is None:
            logging.error("%s: The row_dict cannot be None", STEP)
            raise TypeError("row_dict cannot be None")
        row_value = row_dict.get(column_name)
        if (row_value is None):
            logging.error("%s: The column does not exist", STEP)
            raise TypeError("column name cannot be None")
        values.append(row_dict.get(column_name))

    sorted_values = sorted(values, key=float, reverse=True)
    values_dict = dict([("Maximum", _max(sorted_values)),
                        ("Minimum", _min(sorted_values)),
                        ("Median", _median(sorted_values))])

    _write_to_file(jsonfile, values_dict)


def _median(sorted_values):
        if sorted_values is None:
            logging.error("%s: The sorted_values list cannot be None", STEP)
            raise TypeError("sorted_values list cannot be None")
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
            logging.error("%s: The sorted_values list cannot be None", STEP)
            raise TypeError("sorted_values list cannot be None")
        return float(sorted_values[0])


def _min(sorted_values):
        if sorted_values is None:
            logging.error("%s: The sorted_values list cannot be None", STEP)
            raise TypeError("sorted_values list cannot be None")
        return float(sorted_values[len(sorted_values) - 1])


def _write_to_file(jsonfile, values_dict):
    try:
        with open(jsonfile, "w") as outfile:
            json.dump(values_dict, outfile)
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def print_filesize(directory):
    STEP = "Workflow Step #4"
    logging.info("%s: Printing the filesize to screen.", STEP)

    if directory is None:
        logging.error("%s: The directory does not exist", STEP)
        raise TypeError("Missing directory")

    if not os.path.isdir(directory):
        logging.error("%s: The directory path does not exist, %s",
                      STEP, directory)
        raise IOError("Directory path does not exist")

    try:
        files = os.listdir(directory)
        for a_file in files:
            print "\nfile: " + a_file
            print "size: " + str(os.path.getsize(directory + a_file))
    except IOError as io:
        logging.error("%s: An error has occurred with writing file, %s",
                      STEP, io)


def run():
    logger_config()
    DEFAULT_CONFIG_PATH = APP_DIR_PATH + "/config/workflows.json"
    OUTPUT_DIR = APP_DIR_PATH + "/output/"
    settings = setup(DEFAULT_CONFIG_PATH, OUTPUT_DIR)

    try:
        DEFAULT_WORKFLOW = settings[0].get("operations")
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
