#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core variables that can be accessed by other modules
#
################################################################################

import shutil
from pathlib import Path

import testing_functions

################################################################################
# all primary environment values and functions are accessed here
################################################################################

class main():
    headers_ = []
    justify_ = []
    line_parse_delimiter_ = None
    map_ = []
    using_headers_ = None
    width_ = []

    comment_mode_ = []
    elements_ = None
    goto_ = []
    infomsg_ = []
    output_ = []
    read_inline_ = None
    read_path_ = []
    running_ = []
    timer_ = []
    timer_label_ = []
    timer_ts_ = []

    header_mode_ = None
    interactive_ = False
    interactive_prompt_ = '> '
    max_read_depth_ = 5
    source_path_ =  str(Path(__file__).resolve().parent)
    terminal_width_ = shutil.get_terminal_size().columns
    version_ = None

class testing():
    testing_ = []
    test_filename_ = []
    test_f_ = []
    test_pause_ = []
    test_verbose_ = []
    test_pass_ = []
    test_fail_ = []
    reset = testing_functions.reset
    testMessage = testing_functions.testMessage
    testStop = testing_functions.testStop
    debug = testing_functions.debug

class cli():
    ignore_stop_ = None
    ignore_stop_reset_ = None
    verbose_verbose_ = None
    skip_testing_ = None
    test_force_quiet_ = None
    test_force_verbose_ = None

def reset(full_reset = True):
    main.headers_ = setListValue(main.headers_, None)
    main.justify_ = setListValue(main.justify_, None)
    main.line_parse_delimiter_ = '\s\s\s*'
    main.map_ = setListValue(main.map_, None)
    main.using_headers_ = True
    main.width_ = setListValue(main.width_, None)

    if full_reset:
        main.comment_mode_ = setListValue(main.comment_mode_, 0)
        main.elements_ = None
        main.goto_ = setListValue(main.goto_, None)
        main.infomsg_ = setListValue(main.infomsg_, True)
        main.output_ = setListValue(main.output_, True)
        main.read_inline_ = False
        main.read_path_ = setListValue(main.read_path_, None)
        main.running_ = setListValue(main.running_, True)
        main.timer_ = setListValue(main.timer_, False)
        main.timer_label_ = setListValue(main.timer_label_, None)
        main.timer_ts_ = setListValue(main.timer_ts_, None)

        cli.ignore_stop_ = False
        cli.ignore_stop_reset_ = False
        cli.skip_testing_ = False
        cli.test_force_quiet_ = False
        cli.test_force_verbose_ = False

# only update current sandbox environment values
def setListValue(list, value):
    if list == []:
        list = [value]
    else:
        list[-1] = value
    return list

################################################################################
# class methods to set text colors
################################################################################

class ANSI():
    def set_display_attribute(code): return "\33[{attr}m".format(attr = code)
    FG_DEFAULT = set_display_attribute(0)
    FG_RED = set_display_attribute(31)
    FG_YELLOW = set_display_attribute(33)
    FG_GREEN = set_display_attribute(32)
