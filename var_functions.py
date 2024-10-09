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
from dateutil import parser

import core

################################################################################
# user-definable variables
################################################################################

def process_until(line):
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

def type_by_value(var_value):
    if str(var_value).startswith('date:'):
        try:
            datestr = var_value.replace('date:', '')
            return parser.parse(datestr)
        except ValueError:
            pass

    try:
        return int(var_value)
    except ValueError:
        pass

    try:
        return float(var_value)
    except ValueError:
        pass

    return var_value.strip("'").strip('"')

def get_var(var_key):
    return core.Main.variables_[-1][var_key]

def set_var(var_key, var_values):
    keys = split_string(var_key)
    if len(keys) == 1:
        core.Main.variables_[-1][keys[0]] = [type_by_value(value) for value in var_values]
    elif len(keys) == len(var_values):
        for i, key in enumerate(keys):
            core.Main.variables_[-1][key] = [type_by_value(value) for value in split_string(var_values[i])]
    else:
        raise ValueError()

def check_var(var_key):
    return bool(var_key in core.Main.variables_[-1])

def push_var(var_key, var_values):
    core.Main.variables_[-1][var_key] = [type_by_value(value) for value in core.Main.variables_[-1][var_key] + var_values]

def push_or_set_var(var_key, var_values):
    if check_var(var_key):
        push_var(var_key, var_values)
    else:
        set_var(var_key, var_values)

def pop_var(var_key):
    core.Main.variables_[-1][var_key] = core.Main.variables_[-1][var_key][:-1]

def dup_var(var_key, new_var_keys):
    for new_var_key in new_var_keys:
        set_var(new_var_key, core.Main.variables_[-1][var_key].copy())

def show_var(var_keys):
    keys = split_string(var_keys)
    display_entries = []
    for key in keys:
        if check_var(key):
            display_entries += [f"{key}: {get_var(key)}"]
        else:
            display_entries += [f"{key}: deleted or not found"]
    return display_entries

def show_all_vars():
    display_entries = []
    for var_key in core.Main.variables_[-1]:
        display_entries += show_var(var_key)
    return display_entries

def del_var(var_keys):
    for var_key in var_keys:
        keys = split_string(var_key)
        for key in keys:
            core.Main.variables_[-1].pop(key, None)

def split_string(string):
    return re.split(r'[,\s]\s*', string.strip())

def all_vars():
    return core.Main.variables_[-1].items()
