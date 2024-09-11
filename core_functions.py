#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core Functions
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import fileinput
import glob
import re
import sys
import textwrap
import time
import traceback
from os.path import dirname, exists, realpath

import core
import bridge

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
    if is_float(element) and not is_integer(element):
        formats = core.Main.formats_[-1][index]
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
    if align == '|' or align == '^':
        return cjustify(str(element), core.Main.width_[-1][index], padding) + core.Main.margin_
    if align == '>':
        return rjustify(str(element), core.Main.width_[-1][index], padding) + core.Main.margin_

def ljustify(content, width, padding = ' '):
    return content.ljust(width, padding)[:width]

def cjustify(content, width, padding = ' '):
    return content.center(width, padding)[:width]

def rjustify(content, width, padding = ' '):
    return content.rjust(width, padding)[:width]

def currency(num):
    try:
        return core.Main.currency_format_.format(num)
    except:
        if core.Cli.verbose_verbose_:
            error_message(f"Currency error: {num}, {core.Main.currency_format_}")
            traceback.print_exc()
            core.Main.running_[-1] = False
            pop_env()
        return 'ERROR'

def percentage(num):
    try:
        return core.Main.percentage_format_.format(num)
    except:
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
    except:
        return False

def is_float(num):
    try:
        float(num)
        return True
    except:
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
#    - Data elements are delimited by two spaces.
#    - A dash denotes an empty data element.
################################################################################

def get_elements(line):
    # non-printable null character for internal parsing
    delim = '\x00'

    # convert the delimiter into delim and split the line into elements
    # this approach allows multi-character delimiters
    line = re.sub(core.Main.line_parse_delimiter_, delim, line.lstrip())
    core.Main.elements_ = line.split(delim)

    # dashes are placeholders for empty fields
    for i, element in enumerate(core.Main.elements_):
        if element == core.Main.line_element_placeholder_:
            core.Main.elements_[i] = ' '

    # now we have the elements to send back
    return core.Main.elements_

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
        m = re.search(r'^(#?)([~$%]*)(.*[a-zA-Z])([<|^>]?)(\d+)(\D?)$', element)

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
        if not core.Main.interactive_:
            core.Main.running_[-1] = False
            pop_env()
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
# parse primary directives
################################################################################

def is_directive(line):
    return re.search(r'^\s*&', line)

class Parser:
    # parser class to be set up as an object that can be used by plugins

    def __init__(self):
        self.arg = None
        self.argtrim = None
        self.cmd = None
        self.done = True
        self.line = None
        self.m = None
        self.options = None
        self.usage = None

    def parse_directive(self, line):
        self.pre_parse_directive(line)
        if not self.done:
            if self.usage:
                self.invalid_usage()
            else:
                self.line = line
                self.invalid_directive()

    def parse_setting(self, setting, arg):
        # standardized parsing of the &set directive
        # the calling function guarantees a value parameter

        # &set <setting> "<value>"
        m = re.search(r'^.*' + setting + r'\s\"(.*)\"$', arg)

        # &set <setting> '<value>'
        if m is None:
            m = re.search(r'^.*' + setting + r'\s\'(.*)\'$', arg)

        # &set <setting> <value>
        if m is None:
            m = re.search(r'^.*' + setting + r'\s(.*)$', arg)

        # return the value
        return m.group(1)

    def invalid_directive(self):
        error_message(f"Invalid directive: {self.line}")

    def invalid_usage(self, plugin_usage = None):
        if self.usage is not None:
            general = 'General ' if self.usage is not None and plugin_usage is not None else ''
            error_message(f"{general}Usage: {self.usage}")
        if plugin_usage is not None:
            plugin = 'Plugin ' if self.usage is not None and plugin_usage is not None else ''
            error_message(f"{plugin}Usage: {plugin_usage}")

    def pre_parse_directive(self, line):
        self.line = line
        arg = None
        argtrim = None
        options = []
        m = re.search(r'^\s*\S(cli)\s(.*)$', line)
        if m:
            arg = m.group(2)
            argtrim = arg.strip()
        else:
            m = re.search(r'^\s*\S(\S*)\s(.*)$', line)
            if m:
                arg = m.group(2)
                argtrim = arg.strip()
                while arg.startswith('-'):
                    options.append(argtrim.split()[0])
                    # trim the option and remove one space after it
                    arg = re.sub(r'^\s*' + options[-1], '', arg)
                    arg = re.sub(r'^\s', '', arg)
                    # trim the option and remove all spaces after it
                    argtrim = re.sub(r'^' + options[-1], '', argtrim)
                    argtrim = argtrim.lstrip()
                if len(options) == 0:
                    options.append('') # insert dummy element
            else:
                m = re.search(r'^\s*\S(\S*)$', line)
        cmd = m.group(1)

        ####################

        if cmd == 'cd':
            no_options_recognized(options)
            core.Main.read_path_[-1] = argtrim
            if core.Main.read_path_[-1]:
                info_message(f"Setting current working directory to '{core.Main.read_path_[-1]}'.")
            else:
                info_message('Resetting current working directory.')

        ####################

        elif cmd == 'cli':
            if argtrim is None:
                # mimic command line result without any parameters
                show_info(True)
            else:
                # insert placeholder
                cli_argv = '. ' + argtrim
                # run the options as if from the command line
                filenames = parse_options(cli_argv.split())
                process_data_from_directive(filenames)

        ####################

        elif cmd == 'goto':
            no_options_recognized(options)
            core.Main.goto_[-1] = argtrim
            if argtrim:
                info_message(f"Skipping to '{core.Main.goto_[-1]}'.")
            else:
                self.invalid_usage('&goto <label>')

        ####################

        elif cmd == 'header':
            if argtrim:
                core.Main.elements_ = get_elements(argtrim)
                core.Main.headers_[-1] = make_headers()
            if core.Main.headers_[-1]:
                core.Main.header_mode_ = True
                print_header = True
                for option in options:
                    if option in ['-q', '--quiet']:
                        print_header = False
                    else:
                        unrecognized_option(option)
                if print_header:
                    bridge.Plugin.parseLine('  '.join(core.Main.headers_[-1]))
            else:
                error_message('No header information found.')

        ####################

        elif cmd == 'help':
            no_options_recognized(options)
            show_help(argtrim)

        ####################

        elif cmd == 'identify':
            no_options_recognized(options)
            info_message(f"Loaded plugin: {bridge.Plugin.identify()}")

        ####################

        elif cmd == 'map':
            no_options_recognized(options)
            show_usage = False
            if argtrim:
                premap = get_elements(argtrim)
                core.Main.map_[-1] = [None] * len(premap)
                try:
                    for m, element in enumerate(premap):
                        core.Main.map_[-1][int(premap[m]) - 1] = m + 1
                    info_message('Fields were remapped.')
                except ValueError:
                    show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.invalid_usage('&map <int><space><space><int>...')

        ####################

        elif cmd == 'output' and arg == 'on':
            no_options_recognized(options)
            core.Main.output_[-1] = True
            info_message('Output mode is on.')
        elif cmd == 'output' and arg == 'off':
            no_options_recognized(options)
            info_message('Output mode is off.')
            core.Main.output_[-1] = False
        elif cmd == 'output':
            no_options_recognized(options)
            self.invalid_usage('&output on|off')

        ####################

        elif cmd == 'print':
            self.done = False
            if argtrim and argtrim.startswith('"'):
                # leading double quote
                argtrim = argtrim[1:]
                arg = argtrim
                if argtrim.endswith('"'):
                    # optional matching double quote
                    argtrim = argtrim[:-1]
                    arg = argtrim
            for option in options:
                if option in ['-f', '--force']:
                    # force print
                    print_line(arg)
                    self.done = True
                else:
                    unrecognized_option(option)
            if not self.done:
                if core.Main.output_[-1]:
                    if arg is not None:
                        print_line(arg)
                    else:
                        print_line()
                else:
                    pass
            self.done = True

        ####################

        elif cmd == 'read':
            if argtrim:
                for option in options:
                    if option in ['-i', '--inline']:
                        core.Main.read_inline_ = True
                    elif option in ['-s', '--sandbox']:
                        core.Main.read_inline_ = False
                    else:
                        unrecognized_option(option)
                read_source = argtrim
                read_sources = read_source.split(' ')
                s = 's' if len(read_sources) > 1 else ''
                inline = ' (inline mode)' if core.Main.read_inline_ else ''
                if core.Main.read_path_[-1]:
                    for i, rs in enumerate(read_sources):
                        read_sources[i] = core.Main.read_path_[-1] + '/' + rs
                if core.Main.max_read_depth_ > 0:
                    core.Main.max_read_depth_ = core.Main.max_read_depth_ - 1
                    info_message(f"Reading file{s}: {read_source}{inline}")
                    push_env()
                    try:
                        with fileinput.FileInput(files=(read_sources), mode='r') as read_lines:
                            for read_line in read_lines:
                                read_line = re.sub('\n', '', read_line)
                                if not skip_line(read_line):
                                    bridge.Plugin.parseLine(read_line)
                                if not core.Main.running_[-1]:
                                    break
                    except FileNotFoundError as e:
                        error_message(f"{cmd}: Input file not found: {e.filename}")
                    except IndexError:
                        error_message(f"{cmd}: Badly formed data: {read_line}", True)
                    except ValueError:
                        error_message(f"{cmd}: Invalid input: {read_line}", True)
                    except:
                        error_message(f"{cmd}: Unexpected error.", True)
                        traceback.print_exc()
                    finally:
                        if core.Testing.testing_[-1]:
                            core.Testing.testStop()
                        pop_env()
                        info_message(f"Finished reading file{s}: {read_source}{inline}")
                    core.Main.max_read_depth_ = core.Main.max_read_depth_ + 1
                else:
                    error_message(f"{cmd}: Nested level too deep; will not read {read_source}.")
            else:
                self.invalid_usage('&read <filenames>')

        ####################

        elif cmd == 'set':
            no_options_recognized(options)
            show_usage = False
            if argtrim:
                parts = argtrim.split()
                if len(parts) > 1:
                    if parts[0] == 'currency':
                        core.Main.currency_format_ = self.parse_setting('currency', arg)
                    elif parts[0] == 'percentage':
                        core.Main.percentage_format_ = self.parse_setting('percentage', arg)
                    elif parts[0] == 'margin':
                        core.Main.margin_ = self.parse_setting('margin', arg)
                    elif parts[0] == 'prompt':
                        core.Main.interactive_prompt_ = self.parse_setting('prompt', arg)
                    else:
                        show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.done = False
                self.usage = '&set [ prompt <string> ]'

        ####################

        elif cmd == 'stop':
            no_options_recognized(options)

            # --ignore-stop: continue reading data and ignore the &stop directive
            # otherwise, stop testing and stop running
            if not core.Cli.ignore_stop_:
                if core.Testing.testing_[-1]:
                    core.Testing.testStop()
                core.Main.running_[-1] = False

            # --ignore-stop-reset: same as --ignore-stop, but also reset all running values
            if core.Cli.ignore_stop_reset_:
                if core.Testing.testing_[-1]:
                    core.Testing.testStop()
                core.reset()
                core.Testing.reset()
                bridge.Plugin.reset()

        ####################

        elif cmd == 'timer':
            no_options_recognized(options)
            if argtrim is not None:
                label = ''
                for element in argtrim.split():
                    if element in ['start', 'stop']:
                        mode = element
                    else:
                        label = element
                if mode == 'start':
                    timer_start(label)
                elif mode == 'stop':
                    timer_stop()
            else:
                timer_status()

        ####################

        elif cmd == 'use':
            if argtrim is not None:
                quiet = False
                for option in options:
                    if option in ['-q']:
                        quiet = True
                    else:
                        unrecognized_option(option)
                core.reset(False)
                use_plugin(argtrim)
                if not quiet:
                    parser.parse_directive('&identify')
            else:
                parser.parse_directive('&identify')
                plugins = glob.glob(core.Main.source_path_ + '/plugins/*.py')
                plugins.sort()
                out = ''
                for plugin in plugins:
                    m = re.search(r'^.*\/([\S\s]*).py', plugin)
                    name = m.group(1)
                    if name != bridge.Plugin.identify():
                        out += name + '  '
                info_message(f"Also available:  {out.strip()}")

        ####################

        elif cmd == 'test' and core.Cli.skip_testing_:
            no_options_recognized(options)
        elif cmd == 'test':
            no_options_recognized(options)
            if argtrim is None:
                core.Testing.testMessage(f"Usage: &{cmd} <parameters>")
            elif argtrim.startswith('start'):
                if not core.Testing.testing_[-1]:
                    m = re.search(r'^start\s+(\S*)$', argtrim)
                    if m:
                        core.Testing.test_filename_[-1] = m.group(1)
                        core.Testing.testing_[-1] = True
                        core.Testing.test_pause_[-1] = False
                        core.Testing.test_pass_[-1] = 0
                        core.Testing.test_fail_[-1] = 0
                        core.Testing.testMessage(f"Test started with {core.Testing.test_filename_[-1]}")
                    else:
                        core.Testing.testMessage('Test filename not specified.')
                else:
                    core.Testing.testMessage(f"Test is already running ({core.Testing.test_filename_[-1]}).")
            elif argtrim == 'pause':
                if core.Testing.testing_[-1]:
                    core.Testing.test_pause_[-1] = True
                    core.Testing.testMessage('Test paused.')
                else:
                    core.Testing.testMessage('No test is currently running.')
            elif argtrim == 'resume':
                if core.Testing.testing_[-1]:
                    core.Testing.test_pause_[-1] = False
                    core.Testing.testMessage('Test resumed.')
                else:
                    core.Testing.testMessage('No test is currently running.')
            elif argtrim == 'verbose':
                if not core.Cli.test_force_quiet_:
                    core.Testing.test_verbose_[-1] = True
                    core.Testing.testMessage('Test mode set to verbose.')
            elif argtrim.startswith('versions'):
                m = re.search(r'^versions\s+(.*)$', argtrim)
                if m:
                    version_range = m.group(1)
                    core.Testing.testVersions(version_range)
                else:
                    core.Testing.testMessage('Version range not specified.')
            elif argtrim == 'quiet':
                if not core.Cli.test_force_verbose_:
                    core.Testing.test_verbose_[-1] = False
                    core.Testing.testMessage('Test mode set to quiet.')
            elif argtrim == 'stop':
                core.Testing.testStop()
            else:
                core.Testing.testMessage(f"{cmd}: invalid parameter.")

        ####################

        elif cmd == 'debug':
            fullname = False
            for option in options:
                if option in ['-fn', '--full-name']:
                    fullname = True
                else:
                    unrecognized_option(option)
            core.Testing.debug(argtrim, fullname)

        ####################

        elif cmd == 'infomsg' and arg == 'on':
            quiet = False
            for option in options:
                if option in ['-q']:
                    quiet = True
                else:
                    unrecognized_option(option)
            core.Main.infomsg_[-1] = True
            if not quiet:
                info_message('Infomsg mode is on.')
        elif cmd == 'infomsg' and arg == 'off':
            core.Main.infomsg_[-1] = False

        ####################

        else:
            self.done = False

        self.arg = arg
        self.argtrim = argtrim
        self.cmd = cmd
        self.m = m
        self.options = options

################################################################################
# process command-line options
################################################################################

def parse_options(argv = sys.argv):
    if len(argv) == 1:
        return
    input_files = []
    skip = False
    for i, option in enumerate(argv):
        if skip:
            skip = False
            continue
        if option.startswith('-'):
            if option in ['-is', '--ignore-stop']:
                core.Cli.ignore_stop_ = True
            elif option in ['-isr', '--ignore-stop-reset']:
                core.Cli.ignore_stop_ = True
                core.Cli.ignore_stop_reset_ = True
            elif option in ['-is0']: # undocumented, for testing purposes
                core.Cli.ignore_stop_ = False
            elif option in ['-isr0']: # undocumented, for testing purposes
                core.Cli.ignore_stop_ = False
                core.Cli.ignore_stop_reset_ = False
            elif option in ['-up', '--use-plugin']:
                if i < len(argv) - 1:
                    plugin_name = argv[i+1]
                    use_plugin(plugin_name)
                    skip = True
                else:
                    error_message(f"Parameter expected: {option}")
                    print_line()
                    show_help('usage', True)
            elif option in ['-vv']:
                core.Cli.verbose_verbose_ = True
            elif option in ['-h', '---help']:
                topic = None
                if i < len(argv) - 1:
                    topic = argv[i+1]
                    skip = True
                show_help(topic, True)
            elif option in ['-st', '--skip-testing']:
                core.Cli.skip_testing_ = True
            elif option in ['-tv', '--test-verbose']:
                parser.parse_directive('&test verbose')
            elif option in ['-tfv', '--test-force-verbose']:
                core.Cli.test_force_verbose_ = True
                parser.parse_directive('&test verbose')
            elif option in ['-tfq', '--test-force-quiet']:
                core.Cli.test_force_quiet_ = True
                parser.parse_directive('&test quiet')
            else:
                if i < len(argv) - 1:
                    parameter = argv[i+1]
                else:
                    parameter = None
                # result[0] = known/unknown
                # result[1] = skip next word (option parameter)
                result = bridge.Plugin.parse_option(option, parameter)
                if not result[0]:
                    error_message(f"Unknown option: {option}")
                    print_line()
                    show_help('usage', True)
                else:
                    skip = result[1]
        elif i > 0:
            input_files.append(option)
    return input_files

def unrecognized_option(option):
    if option != '':
        error_message(f"Unrecognized option: {option}")

def no_options_recognized(options):
    for option in options:
        unrecognized_option(option)

################################################################################
# send data to the plugin for processing (from the &cli directive)
################################################################################

def process_data_from_directive(filenames):
    try:
        for filename in filenames:
            f = open(filename, 'r', encoding='utf-8')
            f_input = f.readlines()
            f.close()
            for line in f_input:
                line = re.sub('\n', '', line)
                if not skip_line(line):
                    bridge.Plugin.parseLine(line)
    except FileNotFoundError as e:
        error_message(f"cli: Input file not found: {e.filename}")
    except IndexError:
        error_message(f"cli: Badly formed data: {line}")
    except ValueError:
        error_message(f"cli: Invalid input: {line}")
    except KeyboardInterrupt:
        error_message('Interrupted.')
    except:
        error_message('Unexpected error.')
        traceback.print_exc()
    finally:
        fileinput.close()

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
        except:
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
        return True
    if core.Main.goto_[-1]:
        return True
    return False

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
        for line in helpfile:
            print(textwrap.fill(line, core.Main.terminal_width_))
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
        core.Main.timer_ts_
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
    push_lists(bridge.Plugin.getEnv())

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
        core.Main.map_
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
    pop_lists(bridge.Plugin.getEnv())

def push_lists(lists):
    if lists is not None:
        for pushlist in lists:
            if pushlist is not None:
                pushlist.append(pushlist[-1])

def pop_lists(lists):
    if lists is not None:
        for poplist in lists:
            if poplist is not None and len(poplist) > 1:
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
        print_line('<i> ' + message)

def error_message(message, trace = False):
    print_line(core.ANSI.FG_RED + '<E> ' + message + core.ANSI.FG_DEFAULT, sys.stderr)
    if trace and core.Cli.verbose_verbose_:
        traceback.print_exc()

################################################################################
# must be at the end of this code
################################################################################

parser = Parser()
