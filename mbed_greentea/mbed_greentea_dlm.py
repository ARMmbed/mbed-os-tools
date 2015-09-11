"""
mbed SDK
Copyright (c) 2011-2014 ARM Limited

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: Przemyslaw Wirkus <Przemyslaw.Wirkus@arm.com>
"""

import os
import json
import uuid
import lockfile
from os.path import expanduser

HOME_DIR = expanduser("~")
GREENTEA_HOME_DIR = ".mbed-greentea"
GREENTEA_GLOBAL_LOCK = "glock.lock"
GREENTEA_KETTLE = "kettle.json" # active Greentea instances
GREENTEA_KETTLE_PATH = os.path.join(HOME_DIR, GREENTEA_HOME_DIR, GREENTEA_KETTLE)


def greentea_home_dir_init():
    if not os.path.isdir(os.path.join(HOME_DIR, GREENTEA_HOME_DIR)):
        os.mkdir(os.path.join(HOME_DIR, GREENTEA_HOME_DIR))

def greentea_get_app_sem():
    greentea_home_dir_init()
    gt_instance_uuid = str(uuid.uuid4())   # String version
    gt_file_sem_name = os.path.join(HOME_DIR, GREENTEA_HOME_DIR, gt_instance_uuid)
    gt_file_sem = lockfile.LockFile(gt_file_sem_name)
    return gt_file_sem, gt_file_sem_name, gt_instance_uuid

def greentea_get_target_lock(target_id):
    file_path = os.path.join(HOME_DIR, GREENTEA_HOME_DIR, target_id)
    lock = lockfile.LockFile(file_path)
    return lock

def greentea_get_global_lock():
    file_path = os.path.join(HOME_DIR, GREENTEA_HOME_DIR, GREENTEA_GLOBAL_LOCK)
    lock = lockfile.LockFile(file_path)
    return lock


def greentea_update_kettle(greentea_uuid):
    from time import gmtime, strftime

    with greentea_get_global_lock():
        current_brew = get_json_data_from_file(GREENTEA_KETTLE_PATH)
        if not current_brew:
            current_brew = {}
        current_brew[greentea_uuid] = {
            "start_time" : strftime("%Y-%m-%d %H:%M:%S", gmtime()),
            "cwd" : os.getcwd(),
            "locks" : []
        }
        with open(GREENTEA_KETTLE_PATH, 'w') as kettle_file:
            json.dump(current_brew, kettle_file, indent=4)

def greentea_clean_kettle(greentea_uuid):
    with greentea_get_global_lock():
        current_brew = get_json_data_from_file(GREENTEA_KETTLE_PATH)
        if not current_brew:
            current_brew = {}
        current_brew.pop(greentea_uuid, None)
        with open(GREENTEA_KETTLE_PATH, 'w') as kettle_file:
            json.dump(current_brew, kettle_file, indent=4)

def greentea_():
    pass

def get_json_data_from_file(json_spec_filename, verbose=False):
    """ Loads from file JSON formatted string to data structure
    """
    result = None
    try:
        with open(json_spec_filename, 'r') as data_file:
            try:
                result = json.load(data_file)
            except ValueError:
                result = None
    except IOError:
        result = None
    return result
