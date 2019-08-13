"""Validate the Platform Database against the online database"""

import sys
import logging
import argparse
import json

import requests

from mbed_os_tools.detect.platform_database import DEFAULT_PLATFORM_DB

_MBED_OS_TARGET_API = "https://os.mbed.com/api/v4/targets"

logger = logging.getLogger(__name__)


def add_product_code(target, product_codes, invalid_product_codes, product_code, board_type):
    issue_found = False
    if product_code in product_codes.keys():
        existing_board_type = product_codes[product_code]
        if existing_board_type == board_type:
            logging.warning("Duplicate entry for product code '%s' with identical board types '%s'", product_code, board_type)
            issue_found = True
        elif "PLACEHOLDER" in board_type:
            logging.warning("Duplicate entry for product code '%s' using board type '%s' instead of '%s'", product_code, existing_board_type, board_type)
            issue_found = True
        elif "PLACEHOLDER" in existing_board_type:
            logging.warning("Duplicate entry for product code '%s' using board type '%s' instead of '%s'", product_code, board_type, existing_board_type)
            product_codes[product_code] = board_type
            issue_found = True
        else:
            logging.error("Rejecting product code '%s' due to duplicate entries with differing board types '%s' and '%s'", str(product_code), existing_board_type, board_type)
            invalid_product_codes.add(product_code)
            issue_found = True
    elif not product_code:
        logging.warning("Ignoring entry as product code not defined in:\n%s", str(target))
        issue_found = True
    elif not board_type:
        logging.warning("Ignoring entry as board type not defined in:\n%s", str(target))
        issue_found = True
    else:
        product_codes[product_code] = board_type
    return issue_found


# def get_api_product_codes():
#     """Retrieve list of product codes and board types from the API.
#
#     :return: A dictionary allowing for product code to board type lookups e.g. {<product code> : <board type>}
#     :rtype: dict
#     """
#     error_count = 0
#     target_count = 0
#     product_codes = {}
#     invalid_product_codes = set()
#     response = requests.get(_MBED_OS_TARGET_API)
#
#     if response.status_code == 200:
#         try:
#             json_data = response.json()
#         except ValueError:
#             logging.error("Invalid JSON receieved from %s" % _MBED_OS_TARGET_API)
#         else:
#             try:
#                 target_list = json_data["data"]
#             except KeyError:
#                 logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
#             else:
#                 for target in target_list:
#                     target_count += 1
#                     try:
#                         attributes = target["attributes"]
#                         product_code = attributes["product_code"].upper()
#                         board_type = attributes["board_type"].upper()
#                         error_count += 1
#                     except KeyError:
#                         logging.warning("Incomplete entry in:\n%s", str(target))
#                     else:
#                         if add_product_code(target, product_codes, invalid_product_codes, product_code, board_type):
#                             error_count += 1
#     else:
#         logging.error("Invalid JSON receieved from %s" % _MBED_OS_TARGET_API)
#
#     # Remove invalid product codes from generated dictionary
#     for invalid_product_code in invalid_product_codes:
#         product_codes.pop(invalid_product_code)
#
#     logger.info("%d discrepancies found in %d targets", error_count, target_count)
#
#     return product_codes


def get_api_product_codes():
    product_codes = {}
    invalid_product_codes = set()
    error_count = 0
    target_count = 0

    with open("/Users/graham01/Downloads/cool_targets.json", "r") as mbed_os_target:
        json_data = json.loads(mbed_os_target.read())
        try:
            target_list = json_data["data"]
        except KeyError:
            logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
        else:
            for target in target_list:
                target_count += 1
                try:
                    attributes = target["attributes"]
                    product_code = attributes["product_code"].upper()
                    board_type = attributes["board_type"].upper()
                except KeyError:
                    logging.warning("Incomplete entry in:\n%s", str(target))
                    error_count += 1
                else:
                    if add_product_code(target, product_codes, invalid_product_codes, product_code, board_type):
                        error_count += 1

    # Remove invalid product codes from generated dictionary
    for invalid_product_code in invalid_product_codes:
        product_codes.pop(invalid_product_code)

    logger.info("%d discrepancies found in %d targets", error_count, target_count)
    return product_codes


def get_mbed_os_product_codes(mbed_os_targets_path):
    product_codes = {}
    invalid_product_codes = set()

    error_count = 0
    target_count = 0
    with open(mbed_os_targets_path, "r") as mbed_os_target:
        target_dict = json.loads(mbed_os_target.read())

        for board_type, target in target_dict.items():
            try:
                detect_codes = target["detect_code"]
            except KeyError:
                # Ignore entries without product codes
                pass
            else:
                for detect_code in detect_codes:
                    target_count += 1
                    if add_product_code(target, product_codes, invalid_product_codes, detect_code, board_type):
                        error_count += 1
    logger.info("%d discrepancies found in %d targets", error_count, target_count)
    return product_codes


def log_title(title):
    logger.info(title + "\n" + "=" * len("INFO: " + title))


def main():
    """Handle command line arguments to generate a results summary file."""
    parser = argparse.ArgumentParser()

    parser.add_argument("-t", "--targets", type=str, help="Path to Mbed OS targets file (targets.json).")
    parser.add_argument("-v", "--verbose", action='count', default=0, help="Verbosity, by default errors are reported.")
    arguments = parser.parse_args()

    if arguments.verbose > 2:
        log_level = logging.DEBUG
    elif arguments.verbose > 1:
        log_level = logging.INFO
    elif arguments.verbose > 0:
        log_level = logging.WARNING
    else:
        log_level = logging.ERROR

    logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')

    log_title("Processing product codes from os.mbed.com")
    api_product_codes = get_api_product_codes()

    if arguments.targets:
        log_title("Processing product codes from mbed-os")
        mbed_os_product_codes = get_mbed_os_product_codes(arguments.targets)
    else:
        mbed_os_product_codes = {}

    log_title("Validating against mbed-os-tools")
    error_count = 0
    target_count = 0
    for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
        api_board_type = api_product_codes.get(product_code)
        target_count += 1
        if mbed_os_product_codes:
            mbed_os_board_type = mbed_os_product_codes.get(product_code)
            if api_board_type != board_type or mbed_os_board_type != board_type:
                logging.error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s', mbed-os: '%s'", product_code, board_type, api_board_type, mbed_os_board_type)
                error_count += 1
        else:
            if api_board_type != board_type:
                logging.error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s'", product_code, board_type, api_board_type)
                error_count += 1

    logger.info("%d discrepancies found in %d targets", error_count, target_count)

    return error_count


if __name__ == "__main__":
    sys.exit(main())
