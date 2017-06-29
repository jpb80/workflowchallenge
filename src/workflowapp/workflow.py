#!/usr/bin/env python
# coding=utf-8
"""Workflow tool application"""

import os
import logging
import json
import csv
import shutil
import distutils.core
import subprocess
import requests
from requests.exceptions import ConnectionError
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


HOME_PATH = os.path.expanduser("~")
INVENTORY_URL = ("https://raw.githubusercontent.com/enigma-io/" +
                 "workflow-interview-challenge/master/inventory.tsv")
DEFAULT_CONFIG_PATH = "../../config/workflows.json"


def logger_config():
    logging.basicConfig(level=logging.INFO, format=("[###%(levelname)s] "
                                                    "%(asctime)s: "
                                                    "%(filename)s: "
                                                    "%(funcName)s(): "
                                                    "%(lineno)d: "
                                                    "%(message)s"))
    logging.info("Started")


def load_settings(filepath):
    logging.info("Loading configuation settings.")
    settings = dict()
    try:
        with open(filepath, "r") as f:
            settings = json.load(f)
        return settings
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def get_active_workflow(settings):
    logging.info("Loading active workflow.")
    result = 0
    for value in settings:
        if value.get("active") is True:
            result = value.get("id")
            break
    return result


def _output_to_json_file(output_filename, textfile):
    try:
        with open(output_filename, "w") as outfile:
            reader = csv.DictReader(textfile.splitlines(),
                                    delimiter='\t')
            json.dump(list(reader), outfile, ensure_ascii=False,
                      sort_keys=True, indent=4)
    except IOError as io:
        logging.error("An error has occurred with writing file, %s", io)


def get_inventory(url):
    try:
        session = requests.Session()
        session_retries = Retry(total=3,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504 ])
        session.mount('http://', HTTPAdapter(max_retries=session_retries))
        response = session.get(url)
        _output_to_json_file("data.json", response.text)
    except ValueError as ve:
        logging.error("An error with requesting api, %s", ve)
    except requests.exceptions.HTTPError as he:
        logging.error("An httperror has occurred, %s", he)
    except ConnectionError as ce:
        logging.error("Max number of network retries, %s", ce)


def process_inventory(filename):
    with open(filename, "r") as jsonfile:
        inventory = json.load(jsonfile, encoding="utf-8")
    return inventory


def run_statistics_on_column(inventory, column_name):
    values = list()
    def _median(sorted_values):
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
        return float(sorted_values[0])

    def _min(sorted_values):
        return float(sorted_values[len(sorted_values) - 1])

    for row_dict in inventory:
        values.append(row_dict.get(column_name))
    sorted_values = sorted(values, key=float, reverse=True)
    values_dict = dict([("Maximum", str(_max(sorted_values))),
                        ("Minimum", str(_min(sorted_values))),
                        ("Median", str(_median(sorted_values)))])
    with open("stats.json", "w") as outfile:
        json.dump(values_dict, outfile)


def run():
    logger_config()
    settings = load_settings(DEFAULT_CONFIG_PATH)
    ACTIVE_WORKFLOWID = get_active_workflow(settings)

    try:
        get_inventory(INVENTORY_URL)
        inventory = process_inventory("data.json")
        run_statistics_on_column(inventory, "Volume 2015")
        logging.info("It is complete.")
    except ValueError as e:
        logging.error("An error has occurred, %s", e)
