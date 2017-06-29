#!/usr/bin/env python
# coding=utf-8

import os
import argparse
import logging
import json
import csv
import shutil
import distutils.core
import subprocess
import requests


home = os.path.expanduser("~")
INVENTORY_URL = ("https://raw.githubusercontent.com/enigma-io/" +
                 "workflow-interview-challenge/master/inventory.tsv")


def logger_config():

    logging.basicConfig(level=logging.INFO, format=("[###%(levelname)s] "
                                                    "%(asctime)s: "
                                                    "%(filename)s: "
                                                    "%(funcName)s(): "
                                                    "%(lineno)d: "
                                                    "%(message)s"))
    logging.info("Started")


def parse_args_config():

    parser = argparse.ArgumentParser(
        description="WorkflowApp")
#    parser.add_argument("-f", "--inputfile",
#                        required=True, type=str, nargs="+",
#                        help="Load input excel (.xlsx) file.")
#    parser.add_argument("-t", "--type", required=True,
#                        choices=['translations', 'modules'],
#                        type=str, nargs="+",
#                        help="Choose either 'translations' or 'modules'.")
    return parser


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
        response = requests.get(url)
        response.raise_for_status()
        _output_to_json_file("data.json", response.text)
    except ValueError as ve:
        logging.error("An error with requesting api, %s", ve)
    except requests.exceptions.HTTPError as he:
        logging.error("An httperror has occurred, %s", he)


# [{
# "Volume 2015": {
#   "Minimum": "2",
#   "Maximum": "32",
#   "Median": "36"
# }
# }]
#
def process_inventory(filename):
    with open(filename, "r") as jsonfile:
        inventory = json.load(jsonfile, encoding="utf-8")
    return inventory


def run_statistics_on_column(inventory, column_name):
    values = list()
    for row_dict in inventory:
        values.append(row_dict.get(column_name))
    sorted_values = sorted(values, key=float, reverse=True)
    values_dict = dict([("Maximum", str(_max(sorted_values))),
                        ("Minimum", str(_min(sorted_values))),
                        ("Median", str(_median(sorted_values)))])
    with open("stats.json", "w") as outfile:
        json.dump(values_dict, outfile)


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


def main():

    logger_config()
    parser = parse_args_config()
    args = parser.parse_args()
    args_list = vars(args)
    try:
        get_inventory(INVENTORY_URL)
        inventory = process_inventory("data.json")
        run_statistics_on_column(inventory, "Volume 2015")
        logging.info("It is complete.")
    except ValueError as e:
        print(e.args)

if __name__ == "__main__":
    main()
