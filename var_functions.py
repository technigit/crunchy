#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core functions to handle variables and associated operations
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import re
from datetime import datetime
from dateutil import parser

import core
import bridge

# non-printable null characters for internal parsing
SPACE_DELIM = '\x00'
COMMA_DELIM = '\x01'

################################################################################
# function support for user-definable variables
################################################################################

def process_until(line):
    # slot values into variable(s) specified by key(s)

    keys = split_string(core.Main.until_var_key_)
    values = split_string(line)
    i = 0
    while i < len(values):
        for key in keys:
            if i < len(values):
                value = values[i]
            else:
                value = 0
            if value == '':
                value = 0
            push_or_set_var(key, [value])
            i += 1

########################################

def get_values(line):
    # get a list of comma-delimited space-delimited values

    pattern = r'(["\'])(.*?)\1'
    result = re.sub(pattern, lambda m: m.group(1) + m.group(2).replace(' ', SPACE_DELIM).replace(',', COMMA_DELIM) + m.group(1), line)
    return result.split()

########################################

def type_by_value(var_value):
    # convert string values to types based on value patterns

    # list
    if isinstance(var_value, list):
        return var_value

    # datetime
    if isinstance(var_value, str):
        var_value = var_value.strip("'").strip('"').replace(SPACE_DELIM, ' ').replace(COMMA_DELIM, ',')
    if str(var_value).startswith('date:') or str(var_value).startswith('@'):
        try:
            datestr = var_value.replace('date:', '').replace('@', '')
            return parser.parse(datestr)
        except ValueError:
            pass
    if isinstance(var_value, datetime):
        return var_value

    # integer
    try:
        int_value = int(var_value)
        if str(int_value) == str(var_value):
            return int_value
    except ValueError:
        pass

    # float
    try:
        float_value = float(var_value)
        if str(float_value) == str(var_value):
            return float_value
    except ValueError:
        pass

    # other
    return var_value

########################################

def get_var(var_key):
    # retrieve variable by key

    var = core.Main.variables_[-1][var_key]
    for i,element in enumerate(var):
        if isinstance(element, datetime):
            var[i] = element.strftime(core.Main.datetime_format_)
    return var

########################################

def set_var(var_key, var_values):
    # store values into a variable by key(s)

    var_keys = split_string(var_key)
    if len(var_keys) == 1:
        if len(var_values) == 1:
            var_values = [type_by_value(value) for value in split_string(var_values[0])]
        else:
            var_values = [value.replace(',', '') if isinstance(value, str) else value for value in var_values]
        core.Main.variables_[-1][var_keys[0]] = [type_by_value(value) for value in var_values]
    elif len(var_keys) == len(var_values):
        for i, this_var_key in enumerate(var_keys):
            core.Main.variables_[-1][this_var_key] = [type_by_value(value) for value in split_string(var_values[i])]
    else:
        raise ValueError()

########################################

def check_var(var_key):
    # check whether a key exists in the variables pool

    return bool(var_key in core.Main.variables_[-1])

########################################

def push_var(var_key, var_values):
    # push a value onto a list variable

    if check_var(var_key):
        core.Main.variables_[-1][var_key] = [type_by_value(value) for value in core.Main.variables_[-1][var_key] + var_values]

########################################

def push_or_set_var(var_key, var_values):
    # push if the variable exists, set otherwise

    if check_var(var_key):
        push_var(var_key, var_values)
    else:
        set_var(var_key, var_values)

########################################

def pop_var(var_key):
    # remove a value from the end of a list variable

    keys = split_string(var_key)
    for key in keys:
        if check_var(key):
            core.Main.variables_[-1][key] = core.Main.variables_[-1][key][:-1]

########################################

def dup_var(var_key, new_var_keys):
    # make duplicates of variable(s)

    if check_var(var_key):
        if len(new_var_keys) > 0:
            for new_var_key in new_var_keys:
                for new_key in split_string(new_var_key):
                    set_var(new_key, core.Main.variables_[-1][var_key].copy())
        else:
            raise ValueError()
    else:
        var_keys = split_string(var_key)
        if len(new_var_keys) == 1:
            new_var_keys = split_string(new_var_keys[0])
        if len(var_keys) == len(new_var_keys):
            for i, this_var_key in enumerate(var_keys):
                if check_var(this_var_key):
                    set_var(new_var_keys[i], core.Main.variables_[-1][this_var_key].copy())
        else:
            raise ValueError()

########################################

def show_var(var_keys):
    # show the contents of variable(s)

    keys = split_string(var_keys)
    display_entries = []
    for key in keys:
        if check_var(key):
            display_entries += [f"{key}: {get_var(key)}"]
        else:
            display_entries += [f"{key}: deleted or not found"]
    return display_entries

########################################

def show_all_vars():
    # show all variables in the variables pool

    display_entries = []
    for var_key in core.Main.variables_[-1]:
        display_entries += show_var(var_key)
    return display_entries

########################################

def del_var(var_keys):
    # delete variable(s)

    for var_key in var_keys:
        keys = split_string(var_key)
        for key in keys:
            core.Main.variables_[-1].pop(key, None)

########################################

def split_string(string):
    # split a string into space-delimited elements

    if isinstance(string, str):
        return re.split(r'[,\s]\s*', string.strip())
    return [string]

########################################

def all_vars():
    # retrieve all variables

    return core.Main.variables_[-1].items()

################################################################################
# var action handling
################################################################################

def var_action(action, argtrim, options):
    # var action routing

    if action == 'capture':
        var_capture(argtrim, options)
    elif action == 'combine':
        var_combine(argtrim, options)
    elif action == 'release':
        var_release(argtrim, options)
    elif action == 'transform':
        var_transform(argtrim, options)
    else:
        return False
    return True

########################################

def var_capture(args, options):
    # configure capture key to capture data into a variable

    core.Main.parser.no_options_recognized(options)
    if core.Main.capture_mode_:
        core.Main.msg.error_message('Please release the current capture first.')
    else:
        core.Main.capture_mode_ = True
        core.Main.capture_key_ = args

########################################

def var_combine(args, options):
    # stub for action to combine captured sets of data

    core.Main.parser.no_options_recognized(options)
    core.Main.msg.info_message(f"&var.combine {options} {args}")

########################################

def var_release(args, options):
    # configure release key to release captured data into the data stream

    core.Main.parser.no_options_recognized(options)
    core.Main.capture_mode_ = False
    core.Main.capture_key_ = None
    core.Main.release_key_ = args

########################################

def var_transform(args, options):
    # stub for action to transform captured data

    core.Main.parser.no_options_recognized(options)
    core.Main.msg.info_message(f"&var.transform {options} {args}")

########################################

def process_release():
    # check for a release key and release the corresponding captured data

    if check_var(core.Main.release_key_):
        captures = get_var(core.Main.release_key_)
        for capture in captures:
            released_line = '  '.join([element if element != ' ' else '-' for element in capture])
            bridge.Plugin.parse_line(released_line)
    core.Main.release_key_ = None
