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

import testing_functions

################################################################################
# all primary environment values and functions are accessed here
################################################################################

class main():
    version_ = None
    running_ = []
    comment_mode_ = []
    interactive_ = False
    infomsg_ = []
    output_ = []
    goto_ = []
    read_path_ = []
    elements_ = None
    headers_ = []
    header_mode_ = None
    justify_ = []
    width_ = []
    map_ = []
    timer_ = []
    timer_label_ = []
    timer_ts_ = []
    max_read_depth_ = 5
    terminal_width_ = shutil.get_terminal_size().columns
    read_inline_ = False

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

def reset():
    main.running_ = [True]
    main.comment_mode_ = [0]
    main.infomsg_ = [True]
    main.output_ = [True]
    main.goto_ = [None]
    main.read_path_ = [None]

    main.elements_ = None
    main.headers_ = [None]
    main.justify_ = [None]
    main.width_ = [None]
    main.map_ = [None]
    main.timer_ = [False]
    main.timer_label_ = [None]
    main.timer_ts_ = [None]

    cli.ignore_stop_ = False
    cli.ignore_stop_reset_ = False
    cli.skip_testing_ = False
    cli.test_force_quiet_ = False
    cli.test_force_verbose_ = False

################################################################################
# class methods to set text colors
################################################################################

class ANSI():
    def set_display_attribute(code): return "\33[{attr}m".format(attr = code)
    FG_DEFAULT = set_display_attribute(0)
    FG_RED = set_display_attribute(31)
    FG_YELLOW = set_display_attribute(33)
    FG_GREEN = set_display_attribute(32)
