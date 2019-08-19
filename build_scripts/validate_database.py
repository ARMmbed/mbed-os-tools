"""Validate the Platform Database against the online database and render results as an HTML pages"""

import os
import sys
import logging
import argparse
import json
from collections import defaultdict
import requests
import jinja2
from mbed_os_tools.detect.platform_database import DEFAULT_PLATFORM_DB

logger = logging.getLogger(__name__)

jinja2_env = jinja2.Environment(
    loader=jinja2.PackageLoader('validate_database', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

_MBED_OS_TARGET_API = "https://os.mbed.com/api/v4/targets"

_OS_MBED_COM = "Online Database (os.mbed.com)"
_MBED_OS = "Mbed OS (targets.json)"
_TOOLS = "Tools Platform Database"

DATA_SOURCE_LIST = [_TOOLS, _MBED_OS, _OS_MBED_COM]


class PlatformValidator(object):
    """Validated known target data sources for a consistent Product ID and Board Type."""

    def __init__(self, output_dir, mbed_os_targets_path, show_all, online_database):
        """Retrieve data from all sources.

        TODO: Remove online_database when API includes private boards

        :param str output_dir: The output directory for the generated report.
        :param str mbed_os_targets_path: Path to the targets.json file which is part of the Mbed OS repo.
        :param bool show_all: Whether to show all boards in the report or just the ones with issues.
        :param str online_database: Path to a JSON dump of the online database from os.mbed.com.
        """
        self._output_dir = output_dir
        self._mbed_os_targets_path = mbed_os_targets_path
        self._show_all = show_all
        self._online_database = online_database

        # Global counts of the issues encountered
        self._error_count = 0
        self._warning_count = 0
        self._info_count = 0

        # The current product code being processed
        self._product_code = None
        # The current board type being processed for Mbed OS Tools
        self._tools_board_type = None

        # The results of the analysis - used when rendering the html page
        self._analysis_results = {}

        # Set of all product codes found across all sources
        self._all_product_codes = set()

        # Set of all board types found across all sources
        self._all_board_types = set()

        # Database of product codes and associated board types for each source
        self._product_code_db = {}
        # Database of board types and associated product codes for each source
        self._board_type_db = {}
        # Metadata associate with the source
        self._source_meta_data = {}

        # Retrieve data from the os.mbed.com API and add to the overall set of product codes
        self._retrieve_platform_data(_OS_MBED_COM, self._os_mbed_com_source)

        # Retrieve data from the Mbed OS repository (targets.json) and add to the overall set of product codes
        self._retrieve_platform_data(_MBED_OS, self._mbed_os_source)

        # Add the local data (in this repo) into the overall set of product codes
        self._retrieve_platform_data(_TOOLS, self._tools_source)

        logger.info("%d unique product codes for %d boards are defined in total", len(self._all_product_codes), len(self._all_board_types))

    def _add_products_and_boards(self, source, product_code_db, board_type_db):
        """Add to the set of all product codes and board types found across all sources.

        :param str source: Name of the data source.
        :param dict product_code_db: A dictionary with product codes as the keys.
        :param dict board_type_db: A dictionary with board types as the keys.
        """
        product_codes = set(product_code_db.keys())
        product_code_count = len(product_codes)
        self._all_product_codes = self._all_product_codes.union(product_codes)

        board_types = set(board_type_db.keys())
        board_type_count = len(board_types)
        self._all_board_types = self._all_board_types.union(board_types)

        self._source_meta_data[source] = {
            "product_code_count": product_code_count,
            "board_type_count": board_type_count,
        }
        self._source_meta_data["*"] = {
            "product_code_count": len(self._all_product_codes),
            "board_type_count": len(self._all_board_types),
        }
        logger.info("%s defines %d product codes for %d board types.", source, product_code_count, board_type_count)

    def _retrieve_platform_data(self, source, data_source_func):
        """Process a remote data source to obtain product codes and board types

        :param str source: Name of the data source.
        :param data_source_func: A function which will yield a (product_code, board_type) tuple.

        :return: A product code database and board type db.
        :rtype: tuple(dict, dict)
        """
        product_code_db = defaultdict(list)
        board_type_db = defaultdict(list)

        for product_code, board_type in data_source_func():
            if product_code and board_type:
                board_type_db[board_type].append(product_code)
                product_code_db[product_code].append(board_type)

        self._product_code_db[source] = product_code_db
        self._board_type_db[source] = board_type_db
        self._add_products_and_boards(source, product_code_db, board_type_db)

        return product_code_db, board_type_db

    @staticmethod
    def _tools_source():
        """Yield target data from the platform database of this repo
        :return: Yield a series of (<product code> : <board type>) tuples
        :rtype: tuple(str, str)
        """
        for product_code, board_type in DEFAULT_PLATFORM_DB["daplink"].items():
            yield product_code, board_type

    def _os_mbed_com_source(self):
        """Yield target data from the database hosted on os.mbed.com API.

        Also handles target data from a temporary file which includes private targets as they not currently available
        from os.mbed.com

        TODO: Remove file option when API returns private targets

        :return: Yield a series of (<product code> : <board type>) tuples
        :rtype: tuple(str, str)
        """
        if self._online_database:
            with open(self._online_database, "r") as mbed_os_target:
                json_data = json.loads(mbed_os_target.read())
                try:
                    target_list = json_data["data"]
                except KeyError:
                    logging.error("Invalid JSON received from local file")
                else:
                    for target in target_list:
                        attributes = target.get("attributes", {})
                        product_code = attributes.get("product_code", "").upper()
                        board_type = attributes.get("board_type", "").upper()
                        yield product_code, board_type
        else:
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
                            attributes = target.get("attributes", {})
                            product_code = attributes.get("product_code", "").upper()
                            board_type = attributes.get("board_type", "").upper()
                            yield product_code, board_type

    def _mbed_os_source(self):
        """Yield target data from GitHub ARMmbed/mbed-os/targets/targets.json
        :return: Yield a series of (<product code> : <board type>) tuples
        :rtype: tuple(str, str)
        """
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
                            yield detect_code, board_type

    def _add_board_types(self, os_mbed_com_board_types, mbed_os_board_types, tools_board_type):
        """Initialise the analysis results with the board types and placeholder keys for this product code.

        :param list os_mbed_com_board_types: List of board types from os.mbed.com.
        :param list mbed_os_board_types: List of board types from Mbed OS.
        :param str tools_board_type: List of board types from Tools.
        """
        initial_value = {
            "product_code": self._product_code,
            "messages": [],
            "status": {
                _OS_MBED_COM: "ok",
                _MBED_OS: "ok",
                _TOOLS: "ok",
            },
            "board_types": {
                _OS_MBED_COM: os_mbed_com_board_types,
                _MBED_OS: mbed_os_board_types,
                _TOOLS: [tools_board_type] if tools_board_type is not None else [],
            },
        }
        self._analysis_results[self._product_code] = initial_value

    def _add_message(self, sources, message, error=False, warning=False):
        """Add message, update source status for product code and update error counts.

        :param str,list sources: Single data source or list of data sources to which the message pertains.
        :param str message: The text of the message.
        :param bool error: Set to True if this is anerror message.
        :param bool warning: Set to True if this is a warning message.
        """
        results_for_product_code = self._analysis_results[self._product_code]

        # Include each source in the message text
        source_list = sources if isinstance(sources, list) else [sources]
        results_for_product_code["messages"].append("%s: %s" % (", ".join(source_list), message))

        # Set the status for each source listed
        for source in source_list:
            if error:
                results_for_product_code["status"][source] = "error"
            elif warning:
                if results_for_product_code["status"][source] != "error":
                    results_for_product_code["status"][source] = "warning"

        # Only increment the counts once for each message
        if error:
            self._error_count += 1
        elif warning:
            self._warning_count += 1
        else:
            self._info_count += 1

    @staticmethod
    def _remove_placeholders(board_types):
        return [board_type for board_type in board_types if "PLACEHOLDER" not in board_type]

    def _check_board_type_list(self, source, board_types):

        if None in board_types:
            self._add_message(source, "Board type value missing.", error=True)

        defined_board_types = self._remove_placeholders(board_types)
        if len(board_types) > 1:
            if len(defined_board_types) == 1:
                self._add_message(_OS_MBED_COM, "Placeholder board type needs to be removed.", warning=True)
            else:
                self._add_message(_OS_MBED_COM, "Board type defined multiple times.", error=True)

    def check_for_mismatches(self, source, board_types):
        defined_board_types = self._remove_placeholders(board_types)
        match = False
        mismatch = False
        if defined_board_types:
            if self._tools_board_type in defined_board_types:
                match = True
            else:
                mismatch = True
        else:
            mismatched_product_codes = self._board_type_db[source][self._tools_board_type]
            if mismatched_product_codes:
                for product_code in mismatched_product_codes:
                    self._add_message(source, "Board type %s is associated with the product code: %s." % (self._tools_board_type, product_code), error=True)
            elif board_types:
                self._add_message(source, "Placeholder should be updated.", warning=True)
            else:
                if self._tools_board_type in self._board_type_db[source].keys():
                    self._add_message(source, "Product code should be added to board definition.", warning=True)
                else:
                    self._add_message(source, "Board type must be added.", error=True)

        # Check if the other board types being listed for this product code (in this data source) are associated with
        # another product code. If these product codes are not also listed for the appropriate board type in the Mbed OS
        # Tools log an error.
        for board_type in defined_board_types:
            if board_type != self._tools_board_type:
                tools_product_codes = self._board_type_db[_TOOLS][board_type]
                for product_code in self._board_type_db[source][board_type]:
                    if product_code not in tools_product_codes and product_code != self._product_code:
                        self._add_message(source, "Board type %s is associated with the product code: %s." % (board_type, product_code), error=True)

        return match, mismatch

    def validate_data_source(self):
        for self._product_code in self._all_product_codes:

            mbed_os_tools_board_types = self._product_code_db[_TOOLS].get(self._product_code)
            if mbed_os_tools_board_types is None:
                self._tools_board_type = None
            else:
                # There will be only one board type for a given product code in Mbed OS Tools due to the data structure
                self._tools_board_type = mbed_os_tools_board_types[0]

            os_mbed_com_board_types = self._product_code_db[_OS_MBED_COM].get(self._product_code, [])
            mbed_os_board_types = self._product_code_db[_MBED_OS].get(self._product_code, [])

            # Initialise analysis results for this product code
            self._add_board_types(os_mbed_com_board_types, mbed_os_board_types, self._tools_board_type)

            # Product code must be alphanumeric, add an error for each source it appears in
            product_code_valid = True
            if not self._product_code.isalnum():
                for source in DATA_SOURCE_LIST:
                    if self._product_code in self._product_code_db[source]:
                        self._add_message(source, "Product code must be alphanumeric.", error=True)
                        product_code_valid = False

            if product_code_valid and self._product_code not in self._product_code_db[_OS_MBED_COM]:
                # If a product code has been found then it absolutely must be in the database, it may or may not be in
                # the other data sources
                self._add_message(_OS_MBED_COM, "Product code must be listed to reserve the number.", error=True)

            self._check_board_type_list(_OS_MBED_COM, os_mbed_com_board_types)
            self._check_board_type_list(_MBED_OS, mbed_os_board_types)

            if self._tools_board_type:
                if "PLACEHOLDER" in self._tools_board_type:
                    self._add_message(_TOOLS, "Placeholder board type should be removed.", warning=True)
                else:
                    os_mbed_com_match, os_mbed_com_mismatch = self.check_for_mismatches(_OS_MBED_COM, os_mbed_com_board_types)
                    mbed_os_match, mbed_os_mismatch = self.check_for_mismatches(_MBED_OS, mbed_os_board_types)

                    if os_mbed_com_mismatch and mbed_os_mismatch:
                        self._add_message(_TOOLS, "Board type incorrectly defined.", error=True)
                    elif os_mbed_com_mismatch:
                        if mbed_os_match:
                            self._add_message(_OS_MBED_COM, "Board type incorrectly defined.", error=True)
                        else:
                            self._add_message([_OS_MBED_COM, _TOOLS], "Board types do not match.", error=True)
                    elif mbed_os_mismatch:
                        if os_mbed_com_match:
                            self._add_message(_MBED_OS, "Board type incorrectly defined.", error=True)
                        else:
                            self._add_message([_MBED_OS, _TOOLS], "Board types do not match.", error=True)

        logger.info("Errors: %d, Warnings %d, Infos: %d.", self._error_count, self._warning_count, self._info_count)

    def _render_templates(self, template_files, **template_kwargs):
        """Render one or more jinja2 templates.

        The output name is based on the template name (with the final extension removed).

        :param list(str) template_files: List of of template file names.
        :param **dict template_kwargs: Keyword arguments to pass to the render method.
        """
        for template_name in template_files:
            output_name = template_name.rsplit('.', 1)[0]
            output_path = os.path.join(self._output_dir, output_name)
            logger.info("Rendering template from %s to %s" % (template_name, output_path))
            template = jinja2_env.get_template(template_name)
            rendered = template.render(**template_kwargs)
            with open(output_path, "w") as output_file:
                output_file.write(rendered.encode('utf8'))

    def render_results(self):
        """Render summary results page in html."""
        # Setup the key word arguments to pass to the jinja2 template
        template_kwargs = {
            "data_sources": DATA_SOURCE_LIST,
            "analysis_results": self._analysis_results,
            "meta_data": self._source_meta_data,
            "show_all": self._show_all,
            "error_count": self._error_count,
            "warning_count": self._warning_count,
            "info_count": self._info_count,
        }

        # Re-render the index templates to reflect the new verification data.
        self._render_templates(("index.html.jinja2", ), **template_kwargs)


def main():
    """Handle command line arguments to generate a results summary file."""
    parser = argparse.ArgumentParser()

    parser.add_argument("targets", type=str, help="Path to Mbed OS targets file (targets.json).")
    parser.add_argument("-o", "--output-dir", type=str, help="Output directory for the summary report.")
    parser.add_argument("-a", "--show-all", action="store_true", help="Show all boards in report not just issues.")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbosity, by default errors are reported.")

    # TODO: Remove this option when API returns private boards
    parser.add_argument("--online-database", type=str, help="JSON dump of the online database (rather than querying os.mbed.com.")

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

    # Path to the output directory
    if arguments.output_dir is None:
        output_dir = os.getcwd()
    else:
        output_dir = arguments.output_dir

    platform_validator = PlatformValidator(output_dir, arguments.targets, arguments.show_all, arguments.online_database)
    platform_validator.validate_data_source()
    platform_validator.render_results()


if __name__ == "__main__":
    sys.exit(main())
