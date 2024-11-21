#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core variables that can be accessed by other modules
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import shutil
from pathlib import Path

import core_directives
import core_functions
import core_options
import testing_functions

################################################################################
# all primary environment values and functions are accessed here
################################################################################

class Main():
    formats_ = []
    headers_ = []
    justify_ = []
    padding_ = []
    line_element_placeholder_ = None
    line_parse_delimiter_ = None
    map_ = []
    using_headers_ = None
    width_ = []

    capture_mode_ = None
    capture_key_ = None
    release_key_ = None

    comment_mode_ = []
    elements_ = []
    goto_ = []
    infomsg_ = []
    output_ = []
    read_inline_ = None
    read_path_ = []
    running_ = []
    timer_ = []
    timer_label_ = []
    timer_ts_ = []
    until_ = None
    until_var_key_ = None
    variables_ = [{}]

    currency_format_ = '${:,.2f}'
    percentage_format_ = '{:.2f}%'
    datetime_format_ = '%Y-%m-%d'
    header_mode_ = None
    interactive_ = False
    interactive_prompt_ = '> '
    interactive_prompt_focused_ = '>> '
    margin_ = ' '
    max_read_depth_ = 5
    source_path_ =  str(Path(__file__).resolve().parent)
    terminal_width_ = shutil.get_terminal_size().columns
    version_ = ''

    # construct messaging class
    class Messaging:
        info_message = core_functions.info_message
        error_message = core_functions.error_message
    msg = Messaging

    # construct parser class from core_directives, core_functions, and core_options
    parser = core_directives.DirectiveParser
    parser.freeze_history = core_functions.freeze_history
    parser.unfreeze_history = core_functions.unfreeze_history
    parser.no_options_recognized = core_options.no_options_recognized
    parser.parse_options = core_options.parse_options
    parser.unrecognized_option = core_options.unrecognized_option

class Testing():
    testing_ = []
    test_filename_ = []
    test_f_ = []
    test_pause_ = []
    test_verbose_ = []
    test_pass_ = []
    test_fail_ = []
    reset = testing_functions.reset
    testMessage = testing_functions.test_message
    testStop = testing_functions.test_stop
    testVersions = testing_functions.test_versions
    debug = testing_functions.debug
    debug_print = testing_functions.debug_print
    debug_print_mode = None

class Cli():
    ignore_stop_ = None
    ignore_stop_reset_ = None
    verbose_verbose_ = None
    skip_testing_ = None
    test_force_quiet_ = None
    test_force_verbose_ = None

def reset(full_reset = True):
    Main.formats_ = set_list_value(Main.formats_, None)
    Main.headers_ = set_list_value(Main.headers_, None)
    Main.justify_ = set_list_value(Main.justify_, None)
    Main.padding_ = set_list_value(Main.padding_, None)
    Main.line_element_placeholder_ = '-'
    Main.line_parse_delimiter_ = r'\s\s\s*'
    Main.map_ = set_list_value(Main.map_, None)
    Main.using_headers_ = True
    Main.width_ = set_list_value(Main.width_, None)

    if full_reset:
        Main.comment_mode_ = set_list_value(Main.comment_mode_, 0)
        Main.elements_ = None
        Main.goto_ = set_list_value(Main.goto_, None)
        Main.infomsg_ = set_list_value(Main.infomsg_, True)
        Main.output_ = set_list_value(Main.output_, True)
        Main.read_inline_ = False
        Main.read_path_ = set_list_value(Main.read_path_, None)
        Main.running_ = set_list_value(Main.running_, True)
        Main.timer_ = set_list_value(Main.timer_, False)
        Main.timer_label_ = set_list_value(Main.timer_label_, None)
        Main.timer_ts_ = set_list_value(Main.timer_ts_, None)
        Main.until_ = None
        Main.until_var_key_ = None
        Main.variables_ = [{}]

        Cli.ignore_stop_ = False
        Cli.ignore_stop_reset_ = False
        Cli.skip_testing_ = False
        Cli.test_force_quiet_ = False
        Cli.test_force_verbose_ = False

# only update current sandbox environment values
def set_list_value(env_list, value):
    if env_list == []:
        env_list = [value]
    else:
        env_list[-1] = value
    return env_list

################################################################################
# class methods to set text colors
################################################################################

class ANSI():
    @staticmethod
    def set_display_attribute(code):
        return f"\33[{code}m"
    FG_DEFAULT = set_display_attribute(0)
    FG_RED = set_display_attribute(31)
    FG_YELLOW = set_display_attribute(33)
    FG_GREEN = set_display_attribute(32)

    CURSOR_TO_FIRST_COLUMN = '\033[F'
