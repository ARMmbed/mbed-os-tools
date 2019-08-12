"""Validate the Platform Database against the online database"""

import sys
import logging
import argparse

import requests

from mbed_os_tools.detect.platform_database import DEFAULT_PLATFORM_DB

_MBED_OS_TARGET_API = "https://os.mbed.com/api/v4/targets"

logger = logging.getLogger(__name__)


def get_api_product_codes():
    """Retrieve list of product codes and board types from the API.

    :return: A dictionary allowing for product code to board type lookups e.g. {<product code> : <board type>}
    :rtype: dict
    """

    product_codes = {}
    invalid_product_codes = set()
    response = requests.get(_MBED_OS_TARGET_API)

    if response.status_code == 200:
        try:
            json_data = response.json()
        except ValueError:
            logging.error("Invalid JSON receieved from %s" % _MBED_OS_TARGET_API)
        else:
            try:
                target_list = json_data["data"]
            except KeyError:
                logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
            else:
                for target in target_list:
                    try:
                        attributes = target["attributes"]
                        product_code = attributes["product_code"].upper()
                        board_type = attributes["board_type"].upper()
                    except KeyError:
                        logging.warning("Incomplete entry in:\n%s" % str(target))
                    else:
                        if product_code in product_codes.keys():
                            existing_board_type = product_codes[product_code]
                            if existing_board_type == board_type:
                                logging.warning("Duplicate entry for product code '%s' with identical board types '%s'" % (product_code, board_type))
                            elif "PLACEHOLDER" in board_type:
                                logging.warning("Duplicate entry for product code '%s' using board type '%s' instead of '%s'" % (product_code, existing_board_type, board_type))
                            elif "PLACEHOLDER" in existing_board_type:
                                logging.warning("Duplicate entry for product code '%s' using board type '%s' instead of '%s'" % (product_code, board_type, existing_board_type))
                                product_codes[product_code] = board_type
                            else:
                                logging.error("Rejecting product code '%s' due to duplicate entries with differing board types '%s' and '%s'" % (str(product_code), existing_board_type, board_type))
                                invalid_product_codes.add(product_code)
                        elif not product_code:
                                logging.warning("Ignoring entry as product code not defined in:\n%s" % str(target))
                        elif not board_type:
                            logging.warning("Ignoring entry as board type not defined in:\n%s" % str(target))
                        else:
                            product_codes[product_code] = board_type
    else:
        logging.error("Invalid JSON receieved from %s" % _MBED_OS_TARGET_API)

    # Remove invalid product codes from generated dictionary
    for invalid_product_code in invalid_product_codes:
        product_codes.pop(invalid_product_code)

    return product_codes


def main():
    """Handle command line arguments to generate a results summary file."""
    parser = argparse.ArgumentParser()

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

    api_product_codes = get_api_product_codes()

    invalid_entry = False
    for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
        try:
            api_board_type = api_product_codes[product_code]
        except KeyError:
            logging.error("Entry for product code '%s' is not listed in online database" % product_code)
        else:
            if api_board_type != board_type:
                logging.error("Board type differs for product code '%s', API: '%s', mbed-os-tools: '%s'" % (product_code, api_board_type, board_type))

    return int(invalid_entry)


if __name__ == "__main__":
    sys.exit(main())
