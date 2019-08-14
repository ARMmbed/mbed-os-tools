"""Validate the Platform Database against the online database"""

import sys
import logging
import argparse
import json
from collections import defaultdict
import requests

from mbed_os_tools.detect.platform_database import DEFAULT_PLATFORM_DB

_MBED_OS_TARGET_API = "https://os.mbed.com/api/v4/targets"

logger = logging.getLogger(__name__)

UNDEFINED_VALUE = "Undefined"
OS_MBED_COM = "os.mbed.com online database"
MBED_OS = "Mbed OS targets.json"
MBED_OS_TOOLS = "Tools platform database"


class ValidateTargetSources(object):
    """Validated known target data sources for a consistent Product ID and Board Type."""

    def __init__(self, mbed_os_targets_path=None):
        self._mbed_os_targets_path = mbed_os_targets_path
        # Global counts of the issues encountered
        self._error_count = 0
        self._warning_count = 0
        self._info_count = 0
        self.error_count = 0
        self._product_code = None

        self._analysis_results = {}

    def _log_error(self, *args, **kwargs):
        logging.error(*args, **kwargs)
        self.error_count += 1

    def _process_data_source(self, target_data_source):

        product_code_db = defaultdict(list)
        board_type_db = defaultdict(list)
        records = 0
        current_error_count = self.error_count

        for product_code, board_type, record_raw_data in target_data_source():
            records += 1

            if not product_code:
                self._log_error("Ignoring entry as product code not defined in:\n%s", str(record_raw_data))
                board_type_db[board_type].append(UNDEFINED_VALUE)
            elif not board_type:
                self._log_error("Ignoring entry as board type not defined in:\n%s", str(record_raw_data))
                product_code_db[product_code].append(UNDEFINED_VALUE)
            else:
                board_type_db[board_type].append(product_code)
                product_code_db[product_code].append(board_type)
                if product_code in product_code_db.keys():
                    existing_board_type = product_code_db[product_code]
                    if existing_board_type == board_type:
                        self._log_error("Duplicate entry for product code '%s' with identical board types '%s'", product_code, board_type)
                    elif "PLACEHOLDER" in board_type:
                        self._log_error("Duplicate entry for product code '%s' using board type '%s' instead of '%s'", product_code, existing_board_type, board_type)
                    elif "PLACEHOLDER" in existing_board_type:
                        self._log_error("Duplicate entry for product code '%s' using board type '%s' instead of '%s'", product_code, board_type, existing_board_type)
                    else:
                        self._log_error("Rejecting product code '%s' due to duplicate entries with differing board types '%s' and '%s'", str(product_code), existing_board_type, board_type)

        logger.info("%d discrepancies found processing %d records", self.error_count - current_error_count, records)

        return product_code_db, board_type_db

    def _os_mbed_com(self):
        """Yield target data from the database hosted on os.mbed.com"""

        with open("/Users/graham01/Downloads/cool_targets.json", "r") as mbed_os_target:
            json_data = json.loads(mbed_os_target.read())
            try:
                target_list = json_data["data"]
            except KeyError:
                logging.error("Invalid JSON received from %s" % _MBED_OS_TARGET_API)
            else:
                for target in target_list:
                    attributes = target.get("attributes", {})
                    product_code = attributes.get("product_code", "").upper()
                    board_type = attributes.get("board_type", "").upper()
                    yield product_code, board_type, target

    def _mbed_os(self):
        """Yield target data from GitHub ARMmbed/mbed-os/targets/targets.json"""
        if self._mbed_os_targets_path:
            with open(self._mbed_os_targets_path, "r") as mbed_os_target:
                target_dict = json.loads(mbed_os_target.read())

                for board_type, target in target_dict.items():
                    try:
                        detect_codes = target["detect_code"]
                    except KeyError:
                        # Ignore entries without product codes
                        pass
                    else:
                        for detect_code in detect_codes:
                            yield detect_code, board_type, target

    def _add_board_types(self, os_mbed_com_board_types, mbed_os_board_types, mbed_os_tools_board_type):
        initial_value = {
            "messages": [],
            "status": {
                OS_MBED_COM: "ok",
                MBED_OS: "ok",
                MBED_OS_TOOLS: "ok",
            },
            "board_types": {
                OS_MBED_COM: os_mbed_com_board_types,
                MBED_OS: mbed_os_board_types,
                MBED_OS_TOOLS: [mbed_os_tools_board_type],
            },
        }
        self._analysis_results[self._product_code] = initial_value


    def _add_message(self, source, message, error=False, warning=False):

        results_for_product_code = self._analysis_results[self._product_code]

        results_for_product_code["messages"].append("%s: %s" % (source, message))

        if error:
            results_for_product_code["status"][source] = "error"
            self._error_count += 1
        elif warning:
            self._warning_count += 1
            if results_for_product_code["status"][source] != "error":
                results_for_product_code["status"][source] = "warning"
        else:
            self._info_count += 1

    def validate_data_source(self):

        log_title("Processing target data from os.mbed.com")
        os_mbed_com_product_code_db, os_mbed_com_board_type_db = self._process_data_source(self._os_mbed_com)

        log_title("Processing target data from mbed-os")
        mbed_os_product_code_db, mbed_os_board_type_db = self._process_data_source(self._mbed_os)

        log_title("Validating against mbed-os-tools")





        current_error_count = self.error_count
        target_count = 0

        # Create a list of all product codes that have been found in the source data
        os_mbed_com_product_codes = set(os_mbed_com_product_code_db.keys())
        logger.info("%s defines %d product codes", OS_MBED_COM, len(os_mbed_com_product_codes))

        mbed_os_product_codes = set(mbed_os_product_code_db.keys())
        logger.info("%s defines %d product codes", MBED_OS, len(mbed_os_product_codes))

        mbed_os_tools_product_codes = set(DEFAULT_PLATFORM_DB["daplink"].keys())
        logger.info("%s defines %d product codes", MBED_OS_TOOLS, len(mbed_os_tools_product_codes))

        all_product_codes = os_mbed_com_product_codes.union(mbed_os_product_codes.union(mbed_os_tools_product_codes))
        logger.info("%d unique product codes are defined in total", len(all_product_codes))

        for self._product_code in all_product_codes:
            os_mbed_com_board_types = os_mbed_com_product_code_db.get(self._product_code, [])
            mbed_os_board_types = mbed_os_product_code_db.get(self._product_code, [])
            mbed_os_tools_board_type = DEFAULT_PLATFORM_DB["daplink"].get(self._product_code, None)
            self._add_board_types(os_mbed_com_board_types, mbed_os_board_types, mbed_os_tools_board_type)

            if self._product_code not in os_mbed_com_product_codes:
                self._add_message(OS_MBED_COM, "Product code is not listed.", error=True)

            if None in os_mbed_com_board_types:
                self._add_message(OS_MBED_COM, "Board type value missing.", error=True)

            if None in mbed_os_board_types:
                self._add_message(MBED_OS, "Board type value missing.", error=True)

            defined_os_mbed_com_board_types = [board for board in os_mbed_com_board_types if "PLACEHOLDER" not in board]
            if len(os_mbed_com_board_types) > 1:
                if len(defined_os_mbed_com_board_types) == 1:
                    self._add_message(OS_MBED_COM, "Placeholder board type needs to be removed.", warning=True)
                else:
                    self._add_message(OS_MBED_COM, "Board type defined multiple times.", error=True)

            defined_mbed_os_board_types = [board for board in mbed_os_board_types if "PLACEHOLDER" not in board]
            if len(mbed_os_board_types) > 1:
                if len(defined_mbed_os_board_types) == 1:
                    self._add_message(MBED_OS, "Placeholder board type needs to be removed.", warning=True)
                else:
                    self._add_message(MBED_OS, "Board type defined multiple times.", error=True)

            if mbed_os_tools_board_type:
                if "PLACEHOLDER" in mbed_os_tools_board_type:
                    self._add_message(MBED_OS_TOOLS, "Placeholder board type should be removed.", warning=True)
                elif not defined_os_mbed_com_board_types and not defined_mbed_os_board_types:
                    self._add_message(MBED_OS_TOOLS, "Unable to confirm board type is correct.")
                    if os_mbed_com_board_types:
                        self._add_message(OS_MBED_COM, "Placeholder must be updated.", warning=True)
                    else:
                        self._add_message(OS_MBED_COM, "Board type must be added.", warning=True)
                    if mbed_os_board_types:
                        self._add_message(MBED_OS, "Placeholder must be updated.", warning=True)
                    else:
                        self._add_message(MBED_OS, "Board type must be added.", warning=True)

                    os_mbed_com_mismatched_product_codes = os_mbed_com_board_type_db[mbed_os_tools_board_type]

                    if os_mbed_com_mismatched_product_codes:
                        self._add_message(OS_MBED_COM,
                                          "Board type incorrectly listed for a different product code(s) %s." % ",".join(
                                              os_mbed_com_mismatched_product_codes), error=True)

                    mbed_os_mismatched_product_codes = mbed_os_board_type_db[mbed_os_tools_board_type]

                    if mbed_os_mismatched_product_codes:
                        self._add_message(MBED_OS,
                                          "Board type incorrectly listed for a different product code(s) %s." % ",".join(
                                              mbed_os_mismatched_product_codes), error=True)
                else:
                    os_mbed_com_match = False
                    os_mbed_com_mismatch = False
                    mbed_os_match = False
                    mbed_os_mismatch = False
                    os_mbed_com_mismatched_product_codes = set()
                    mbed_os_mismatched_product_codes = set()

                    if defined_os_mbed_com_board_types:
                        if mbed_os_tools_board_type in defined_os_mbed_com_board_types:
                            os_mbed_com_match = True
                        else:
                            for mismatched_board_type in defined_os_mbed_com_board_types:
                                for product_code in os_mbed_com_board_type_db[mismatched_board_type]:
                                    if product_code != self._product_code:
                                        os_mbed_com_mismatched_product_codes.add(product_code)
                            os_mbed_com_mismatch = True

                    if defined_mbed_os_board_types:
                        if mbed_os_tools_board_type in defined_mbed_os_board_types:
                            mbed_os_match = True
                        else:
                            for mismatched_board_type in defined_mbed_os_board_types:
                                for product_code in mbed_os_board_type_db[mismatched_board_type]:
                                    if product_code != self._product_code:
                                        mbed_os_board_type_db.add(product_code)
                            mbed_os_mismatch = True


                    if os_mbed_com_mismatch and mbed_os_mismatch:
                        self._add_message(MBED_OS_TOOLS, "Board type incorrectly defined.", error=True)
                    elif os_mbed_com_mismatch and mbed_os_match:
                        if os_mbed_com_mismatched_product_codes:
                            self._add_message(OS_MBED_COM, "Board type incorrectly listed for a different product code(s) %s." % ",".join(os_mbed_com_mismatched_product_codes), error=True)
                        else:
                            self._add_message(OS_MBED_COM, "Board type incorrectly defined.", error=True)
                    elif os_mbed_com_match and mbed_os_mismatch:
                        if mbed_os_mismatched_product_codes:
                            self._add_message(MBED_OS, "Board type incorrectly listed for a different product code(s) %s." % ",".join(mbed_os_mismatched_product_codes), error=True)
                        else:
                            self._add_message(MBED_OS, "Board type incorrectly defined.", error=True)



        from pprint import pprint

        for product_code, results in self._analysis_results.items():
            if results["messages"]:
                print(product_code)
                pprint(results)
        print(self._error_count, self._warning_count, self._info_count)
        # # Use the mbed-os-tools platform database as the
        # for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
        #     api_board_type = os_mbed_com_product_code_db.get(product_code)
        #     target_count += 1
        #     if mbed_os_product_code_db:
        #         mbed_os_board_type = mbed_os_product_code_db.get(product_code)
        #         if api_board_type != board_type or mbed_os_board_type != board_type:
        #             self._log_error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s', mbed-os: '%s'", product_code, board_type, api_board_type, mbed_os_board_type)
        #     else:
        #         if api_board_type != board_type:
        #             self._log_error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s'", product_code, board_type, api_board_type)
        #
        # logger.info("%d discrepancies found in %d targets", self.error_count - current_error_count, target_count)


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

    log_title("Test from all")
    ValidateTargetSources(arguments.targets).validate_data_source()

    # log_title("Processing product codes from os.mbed.com")
    # api_product_codes = get_api_product_codes()
    #
    # if arguments.targets:
    #     log_title("Processing product codes from mbed-os")
    #     mbed_os_product_codes = get_mbed_os_product_codes(arguments.targets)
    # else:
    #     mbed_os_product_codes = {}
    #
    # log_title("Validating against mbed-os-tools")
    # error_count = 0
    # target_count = 0
    # for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
    #     api_board_type = api_product_codes.get(product_code)
    #     target_count += 1
    #     if mbed_os_product_codes:
    #         mbed_os_board_type = mbed_os_product_codes.get(product_code)
    #         if api_board_type != board_type or mbed_os_board_type != board_type:
    #             logging.error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s', mbed-os: '%s'", product_code, board_type, api_board_type, mbed_os_board_type)
    #             error_count += 1
    #     else:
    #         if api_board_type != board_type:
    #             logging.error("Board type differs for product code '%s' - mbed-os-tools: '%s', os.mbed.com: '%s'", product_code, board_type, api_board_type)
    #             error_count += 1
    #
    # logger.info("%d discrepancies found in %d targets", error_count, target_count)

    # return error_count


if __name__ == "__main__":
    sys.exit(main())
