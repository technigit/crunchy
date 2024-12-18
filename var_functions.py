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

import ast
import re
import statistics
from datetime import datetime

import core
import bridge

# non-printable null characters for internal parsing
SPACE_DELIM = '\x00' # \s
COMMA_DELIM = '\x01' # ,
DQUOTE_DELIM = '\x02' # "
SQUOTE_DELIM = '\x03' # '
LBRACKET_DELIM = '\x04' # [
RBRACKET_DELIM = '\x05' # ]

################################################################################
# function support for user-definable variables
################################################################################

def parse_references(line):
    # find variable references and substitute values for them

    pattern = r'{([a-zA-Z0-9:]+)}'
    line = re.sub(pattern, lambda m: parse_reference(m.group(1)), line)
    return line

def parse_reference(ref):
    # look up a single variable reference and return a value

    if ':' in ref:
        var, function = ref.split(':')
    else:
        var = ref
        function = None
    val = get_var(var)
    numeric_val = [v if isinstance(v, (int, float)) else 0 for v in val]
    result = val
    if function == 'average':
        result = core.Main.float_format_.format(statistics.mean(numeric_val))
    elif function == 'count':
        result = len(val)
    elif function == 'max':
        result = max(numeric_val)
    elif function == 'min':
        result = min(numeric_val)
    elif function == 'reverse':
        val.reverse()
        result = val
    elif function == 'sort':
        val.sort()
        result = val
    elif function == 'stddev':
        result = core.Main.float_format_.format(statistics.stdev(numeric_val))
    if isinstance(result, list) and len(result) == 1:
        result = result[0]
    return str(result)

def process_until(line):
    # slot values into variable(s) specified by key(s)

    keys = split_string(core.Main.until_var_key_)
    values = get_values(line.strip())
    i = 0
    padding = False
    if values is None:
        return
    while i < len(values):
        for key in keys:
            if i < len(values):
                value = values[i]
            else: # more values than expected
                value = 0
                padding = True
            if value == '': # two commas will cause this
                value = 0
            push_or_set_var(key, [value])
            i += 1
    if padding and not core.Main.until_quiet_:
        core.Main.msg.info_message('Padding added to match the expected number of variable keys.')

########################################

def get_values(line):
    # get an array of values from a comma-delimited or space-delimited string with possible quotes or brackets

    # save original copy for error messages
    original_line = line

    # encode disruptive structural characters in quoted elements
    pattern = r'(["\'])(.*?)\1'
    line = re.sub(pattern, lambda m: m.group(1) + m.group(2).replace(' ', SPACE_DELIM).replace(',', COMMA_DELIM).replace('"', DQUOTE_DELIM).replace("'", SQUOTE_DELIM).replace('[', LBRACKET_DELIM).replace(']', RBRACKET_DELIM) + m.group(1), line)

    # add commas to satisfy ast parsing expectations
    line = re.sub(r'\]\[', '],[', line)
    line = re.sub(r',\s+', ',', line)
    line = re.sub(r'\s+', ',', line)

    # check for balanced quotes/brackets and return the parsed version
    quote_balance = line.count("'") % 2 + line.count('"') % 2 # ensure that single quotes and double quotes are paired
    bracket_balance = line.count('[') - line.count(']') # ensure that left and right brackets are equally balanced

    # decode disruptive structural characters
    pattern = r'([^\s\[\]\'\",]+)'
    line = re.sub(pattern, lambda m: f"'{m.group(1)}'" if isinstance(type_by_value(m.group(1)), str) else m.group(1), line)
    line = line.replace(SPACE_DELIM, ' ').replace(COMMA_DELIM, ',').replace(DQUOTE_DELIM, '"').replace(SQUOTE_DELIM, "'").replace(LBRACKET_DELIM, '[').replace(RBRACKET_DELIM, ']').replace('\'"', "'").replace('"\'', "'").replace('\'\'', "'")

    if re.match(r'^@.*$', line) or re.match(r'^date:.*', line):
        line = f'"{line}"' # encapsulate date strings
    if quote_balance + bracket_balance == 0:
        try:
            return ast.literal_eval(f"[{line}]")
        except SyntaxError:
            core.Main.msg.error_message(f"Syntax error: {original_line}")

    # alert on unexpected results from unbalanced quotes/brackets
    if quote_balance != 0:
        core.Main.msg.error_message(f"Unbalanced quotes causing incorrect results: {original_line}")
    if bracket_balance != 0:
        core.Main.msg.error_message(f"Unbalanced brackets causing incorrect results: {original_line}")
    return None

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
            return core.Main.DateUtil.parse(datestr)
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
    # store values into variable(s) by key(s)

    var_keys = split_string(var_key)
    if len(var_keys) == 1:
        core.Main.variables_[-1][var_keys[0]] = [type_by_value(value) for value in var_values]
    else:
        for key in var_keys:
            core.Main.variables_[-1][key] = []
        k = 0
        for this_value in var_values:
            if k >= len(var_keys):
                k = 0
            this_var = [type_by_value(value) for value in split_string(this_value)]
            if isinstance(this_var[0], list):
                core.Main.variables_[-1][var_keys[k]] += this_var[0] # append a list
            else:
                core.Main.variables_[-1][var_keys[k]] += this_var # append a non-list value
            k += 1

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
