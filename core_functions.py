#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core functions to handle general operations
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import re
import readline
import shutil
import sys
import textwrap
import time
import traceback
from os.path import dirname, exists, realpath
from dateutil import parser

import core
import bridge
import var_functions

################################################################################
# show utility information in interactive mode
################################################################################

def show_info(should_show = False):
    if should_show or core.Main.interactive_:
        print_line(f"""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
{core.Main.version_}

To get help, enter &help
To exit interactive mode, use Ctrl-D
""")

def check_interactivity(filenames):
    if filenames is None or filenames == []:
        interactive = sys.stdin.isatty()
    else:
        interactive = False
    return interactive

################################################################################
# text formatting
################################################################################

def format_element(index, elements):
    element = elements[index]
    return format_element_by_value(index, element)

def format_element_by_value(index, element):
    padding = ' '
    formats = core.Main.formats_[-1][index]
    if isinstance(element, str) and '@' in formats:
        try:
            element = parser.parse(element).strftime(core.Main.datetime_format_)
        except ValueError:
            pass
    if is_float(element) and not is_integer(element):
        if not core.Main.header_mode_:
            padding = core.Main.padding_[-1][index]
        if formats is not None:
            if '~' in formats:
                element = str(round(float(element)))
            if '$' in formats:
                element = currency(float(element))
            elif '%' in formats:
                element = percentage(float(element))
    elif element.strip() != '' and not core.Main.header_mode_:
        padding = core.Main.padding_[-1][index]
    align = core.Main.justify_[-1][index]
    if align == '<':
        return ljustify(str(element), core.Main.width_[-1][index], padding) + core.Main.margin_
    if align in ['|', '^']:
        return cjustify(str(element), core.Main.width_[-1][index], padding) + core.Main.margin_
    if align == '>':
        return rjustify(str(element), core.Main.width_[-1][index], padding) + core.Main.margin_
    return element

def ljustify(content, width, padding = ' '):
    return content.ljust(width, padding)[:width]

def cjustify(content, width, padding = ' '):
    return content.center(width, padding)[:width]

def rjustify(content, width, padding = ' '):
    return content.rjust(width, padding)[:width]

def currency(num):
    try:
        return core.Main.currency_format_.format(num)
    except: # pylint: disable=bare-except
        if core.Cli.verbose_verbose_:
            error_message(f"Currency error: {num}, {core.Main.currency_format_}")
            traceback.print_exc()
            core.Main.running_[-1] = False
            pop_env()
        return 'ERROR'

def percentage(num):
    try:
        return core.Main.percentage_format_.format(num)
    except: # pylint: disable=bare-except
        if core.Cli.verbose_verbose_:
            error_message(f"Percentage error: {num}, {core.Main.percentage_format_}")
            traceback.print_exc()
            core.Main.running_[-1] = False
            pop_env()
        return 'ERROR'

def is_integer(num):
    try:
        intnum = int(num)
        return intnum == num
    except: # pylint: disable=bare-except
        return False

def is_float(num):
    try:
        float(num)
        return True
    except: # pylint: disable=bare-except
        return False

################################################################################
# timer
################################################################################

def timer_get_label():
    if core.Main.timer_label_[-1].isdigit():
        return core.Main.timer_label_[-1]
    else:
        return f"'{core.Main.timer_label_[-1]}'"

def timer_put_label(label):
    if label == '':
        label = str(len(core.Main.timer_) - 1)
    core.Main.timer_label_[-1] = label

def timer_start(label = ''):
    timer_put_label(label)
    if core.Main.timer_[-1]:
        info_message(f"Timer {timer_get_label()} is already running.")
    else:
        core.Main.timer_[-1] = True
        core.Main.timer_ts_[-1] = time.time()
        info_message(f"Timer {timer_get_label()} started.")

def timer_stop():
    if not core.Main.timer_[-1]:
        info_message(f"Timer {timer_get_label()} is not running.")
    else:
        core.Main.timer_[-1] = False
        ts = time.time()
        info_message(f"Timer {timer_get_label()} stopped, {timer_elapsed(core.Main.timer_ts_[-1], ts)}")

def timer_status():
    if core.Main.timer_[-1]:
        info_message(f"Timer {timer_get_label()} is running.")
    else:
        info_message(f"Timer {timer_get_label()} is not running.")

def timer_elapsed(start, stop):
    return f"{stop - start:.5f}s"

################################################################################
# process data
#
#    - Data elements delimited by at least two spaces (line_parse_delimiter_).
#    - A dash denotes an empty data element (line_element_placeholder_).
################################################################################

def get_elements(line):
    # non-printable null character for internal parsing
    delim = '\x00'

    # convert the delimiter into delim and split the line into elements
    # this approach allows multi-character delimiters
    line = re.sub(core.Main.line_parse_delimiter_, delim, line.lstrip())
    elements = line.split(delim)

    # dashes are placeholders for empty fields
    for i, element in enumerate(elements):
        if element == core.Main.line_element_placeholder_:
            elements[i] = ' '

    # now we have the elements to send back
    return elements

################################################################################
# generate header data according to specifications
################################################################################

def make_headers():
    # initialize header attributes
    core.Main.formats_[-1] = [None] * len(core.Main.elements_)
    core.Main.justify_[-1] = [None] * len(core.Main.elements_)
    core.Main.padding_[-1] = [None] * len(core.Main.elements_)
    core.Main.width_[-1] = [None] * len(core.Main.elements_)

    # iterate over header specification
    for i, element in enumerate(core.Main.elements_):

        # prepare the element for clean parsing
        element = element.strip()

        # parse the header element specification
        m = re.search(r'^(#?)([~$%@]*)(.*[a-zA-Z])([<|^>]?)(\d+)(\D?)$', element)

        # valid format
        if m is not None:

            # extract specification parameters
            m_comment = m.group(1)
            m_formats = m.group(2)
            m_heading = m.group(3)
            m_justify = m.group(4)
            m_width = m.group(5)
            m_padding = m.group(6)
            if m_justify == '':
                m_justify = '>'
            if m_padding == '':
                m_padding = ' '

            # store specification parameters
            core.Main.elements_[i] = m_comment + m_heading
            core.Main.formats_[-1][i] = m_formats
            core.Main.justify_[-1][i] = m_justify
            core.Main.width_[-1][i] = int(m_width)
            core.Main.padding_[-1][i] = m_padding

        # invalid format
        else:
            return None

    # return extracted headers
    return core.Main.elements_

################################################################################
# process headers
#
#    - Stores elements in core.Main.elements_ for internal processing.
#    - Returns a mapped set of elements if there is an output.
#    - Returns None if there is no output.
################################################################################

def pre_parse(line):
    # break the line down into its constituent parts
    core.Main.elements_ = get_elements(line)

    # &var.capture
    if core.Main.capture_mode_:
        var_functions.push_or_set_var(core.Main.capture_key_, [core.Main.elements_])
        return None

    # current plugin not using headers: done, no mapping needed
    if not core.Main.using_headers_:
        return

    # if we don't have a header yet, then we need to get one now
    if core.Main.headers_[-1] is None:
        core.Main.headers_[-1] = make_headers()
        core.Main.header_mode_ = True

    # if we still don't have a header at this point, then the data is misconfigured
    if core.Main.headers_[-1] is None:
        error_message(f"Invalid header configuration: {line}")
        return

    # return the header or data elements, after mapping
    return map_elements(core.Main.elements_)

################################################################################
# map header/data elements to rearrange "columns" according to specifications
################################################################################

def map_elements(elements):
    out = ''
    for i, _ in enumerate(elements):
        m = i
        if core.Main.map_[-1] is not None:
            m = core.Main.map_[-1][i] - 1
        if not core.Main.headers_[-1][m].startswith('#'):
            out += format_element(m, elements)
    return out

################################################################################
# call use_plugin in the bridge module and catch errors
################################################################################

def use_plugin(plugin_name):
    try:
        bridge.use_plugin(plugin_name)
    except AttributeError:
        error_message(f"{plugin_name}: Incomplete plugin implementation.  Check that all attributes are implemented.", True)
    except ModuleNotFoundError:
        error_message(f"Plugin not found: {plugin_name}", True)

################################################################################
# send content to the output, but run it through testing if required
################################################################################

def print_line(line = '', stdio=sys.stdout):
    if core.Testing.testing_[-1]:
        try:
            if core.Testing.test_f_[-1] is None:
                read_source = core.Testing.test_filename_[-1]
                if core.Main.read_path_[-1]:
                    read_source = core.Main.read_path_[-1] + '/' + core.Testing.test_filename_[-1]
                if exists(read_source):
                    core.Testing.test_f_[-1] = open(read_source, 'r', encoding='utf-8')
                else:
                    core.Testing.testMessage(f"File '{read_source}' does not exist; stopping test.")
                    core.Testing.testStop(True)
            if core.Testing.test_f_[-1] is not None:
                line = re.sub('\n', '', line)
                test_line = core.Testing.test_f_[-1].readline()
                if test_line != '':
                    test_line = re.sub('\n', '', test_line)
                    if line == test_line:
                        core.Testing.testMessage(f"Passed: {line}")
                        core.Testing.test_pass_[-1] += 1
                    else:
                        core.Testing.testMessage(f"Expected: '{test_line}'", True)
                        core.Testing.testMessage(f"Received: '{line}'", True)
                        core.Testing.test_fail_[-1] += 1
                else:
                    core.Testing.testMessage('Unexpected EOF reached; stopping test.', True)
                    core.Testing.testStop(True)
        except: # pylint: disable=bare-except
            core.Testing.testMessage(f"Unexpected error: {line}", True)
            traceback.print_exc()
    if not core.Testing.testing_[-1]:
        print(line, file=stdio)

################################################################################
# process comments and gotos
################################################################################

def skip_line(line):
    if core.Main.comment_mode_[-1] == -1:
        core.Main.comment_mode_[-1] = 0
    if re.search(r'^\s*\/\*', line):
        core.Main.comment_mode_[-1] = 1
    if re.search(r'\*\/\s*$', line):
        core.Main.comment_mode_[-1] = -1
    if core.Main.comment_mode_[-1] != 0:
        return True
    if re.search(r'^\s*\#', line):
        return True
    if re.search(r'^\s*\/\/', line):
        return True
    if re.search(r'^[\s-]*$', line):
        return True
    m = re.search(r'^\s*(\S*)\:\s*$', line)
    if m:
        if m.group(1) == core.Main.goto_[-1]:
            core.Main.goto_[-1] = None
        elif m.group(1) == core.Main.until_:
            core.Main.until_ = None
            keys = core.Main.until_var_key_.split(',')
            for key in keys:
                info_message(var_functions.show_var(key))
            unfreeze_history()
        return True
    if core.Main.goto_[-1]:
        return True
    if core.Main.until_:
        var_functions.process_until(line)
        return True
    return False

################################################################################
# freeze/unfreeze up/down arrow history for focused processes
################################################################################

up_down_arrow_history = []

def freeze_history():
    for i in range(readline.get_current_history_length()):
        up_down_arrow_history.append(readline.get_history_item(i + 1))

def unfreeze_history():
    readline.clear_history()
    for item in up_down_arrow_history:
        readline.add_history(item)

################################################################################
# text pager
################################################################################

def page_text(text):
    freeze_history()
    terminal_width = shutil.get_terminal_size().columns
    terminal_height = shutil.get_terminal_size().lines
    prompt_height = 2
    word_wrap_offset = 5
    page_index = -1
    for line in text:
        if page_index < terminal_height - prompt_height:
            line_length = len(line)
            while line_length >= 0:
                line_length -= terminal_width - word_wrap_offset
                page_index += 1
        else:
            command = input('Help (Press Enter to continue or q to quit): ')
            print(core.ANSI.CURSOR_TO_FIRST_COLUMN + ' ' * terminal_width + '\r', end='')
            if command.lower() == 'q':
                break
            page_index = 0
        print(textwrap.fill(line, terminal_width))
    unfreeze_history()

################################################################################
# process help files
################################################################################

def show_help(topic, stop_running = False):
    helpfile = None
    if not topic:
        topic = 'usage'
    try:
        dir_path = dirname(realpath(__file__))
        help_path = dir_path + '/help/' + re.sub(' ', '-', topic).lower()
        if exists(help_path + '/_main.txt'):
            help_path += '/_main'
        helpfile = open(help_path + '.txt', encoding='utf-8')
        if core.Main.interactive_:
            page_text(helpfile)
        else:
            terminal_width = shutil.get_terminal_size().columns
            for line in helpfile:
                print(textwrap.fill(line, terminal_width))
    except FileNotFoundError:
        error_message(f"No help file for '{topic}' could be found.", True)
    finally:
        if helpfile:
            helpfile.close()
    if stop_running:
        core.Main.running_[-1] = False
        pop_env()

################################################################################
# maintain an environment stack to facilitate nested file reads
################################################################################

def push_env():
    push_lists([
        core.Main.running_,
        core.Main.comment_mode_,
        core.Main.infomsg_,
        core.Main.output_,
        core.Main.goto_,
        core.Main.read_path_,
        core.Main.elements_,
        core.Main.formats_,
        core.Main.headers_,
        core.Main.justify_,
        core.Main.padding_,
        core.Main.width_,
        core.Main.map_,
        core.Main.timer_,
        core.Main.timer_label_,
        core.Main.timer_ts_,
        core.Main.variables_
    ])
    push_lists([
        core.Testing.testing_,
        core.Testing.test_filename_,
        core.Testing.test_f_,
        core.Testing.test_pause_,
        core.Testing.test_verbose_,
        core.Testing.test_pass_,
        core.Testing.test_fail_
    ])
    push_lists(bridge.Plugin.get_env())

def pop_env():
    pop_lists([
        core.Main.running_,
        core.Main.comment_mode_,
        core.Main.infomsg_,
        core.Main.output_,
        core.Main.goto_,
        core.Main.read_path_,
        core.Main.elements_,
        core.Main.formats_,
        core.Main.headers_,
        core.Main.justify_,
        core.Main.padding_,
        core.Main.width_,
        core.Main.map_,
        core.Main.timer_,
        core.Main.timer_label_,
        core.Main.timer_ts_,
        core.Main.variables_
    ])
    pop_lists([
        core.Testing.testing_,
        core.Testing.test_filename_,
        core.Testing.test_f_,
        core.Testing.test_pause_,
        core.Testing.test_verbose_,
        core.Testing.test_pass_,
        core.Testing.test_fail_
    ])
    pop_lists(bridge.Plugin.get_env())

def push_lists(lists):
    if lists is not None:
        for pushlist in lists:
            if pushlist is not None:
                newlist = pushlist[-1]
                if isinstance(newlist, dict):
                    newdict = newlist.copy()
                    pushlist.append(newdict)
                else:
                    pushlist.append(pushlist[-1])

def pop_lists(lists):
    if lists is not None:
        for poplist in lists:
            if poplist is not None:
                if len(poplist) > 1:
                    if not core.Main.read_inline_:
                        poplist.pop()
                    else:
                        copy = poplist[-1]
                        poplist.pop()
                        poplist[-1] = copy

################################################################################
# messaging
################################################################################

def info_message(message):
    if core.Main.infomsg_[-1] and core.Main.output_[-1]:
        if isinstance(message, str):
            message = [message]
        for msg in message:
            print_line('<i> ' + msg)

def error_message(message, trace = False):
    print_line(core.ANSI.FG_RED + '<E> ' + message + core.ANSI.FG_DEFAULT, sys.stderr)
    if trace and core.Cli.verbose_verbose_:
        traceback.print_exc()
