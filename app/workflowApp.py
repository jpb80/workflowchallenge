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
INVENTORY_URL = "https://raw.githubusercontent.com/enigma-io/workflow-interview-challenge/master/inventory.tsv"

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


def get_inventory(url):

    try:
        response = requests.get(url)
        response.raise_for_status()
        inventoryfile_text = response.text
        reader = dict()
        with open("data.json", "w") as outfile:
            reader = csv.DictReader(inventoryfile_text.splitlines(), delimiter='\t')
        json2 = json.dumps(reader, ensure_ascii=False, sort_keys=True, indent=4)

    except ValueError as ve:
        logging.error("An error with requesting api, %s", ve)
    except requests.exceptions.HTTPError as he:
        logging.error("An httperror has occurred, %s", he)


def main():

    logger_config()
    parser = parse_args_config()
    args = parser.parse_args()
    args_list = vars(args)
    try:
        json = get_inventory(INVENTORY_URL)
        logging.info("It is complete.")
    except ValueError as e:
        print(e.args)

if __name__ == "__main__":
    main()
