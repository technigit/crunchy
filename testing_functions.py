#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Testing functions
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import core
import bridge
from core_functions import rjustify

def reset():
    core.Testing.testing_ = [False]
    core.Testing.test_filename_ = [None]
    core.Testing.test_f_ = [None]
    core.Testing.test_pause_ = [False]
    core.Testing.test_verbose_ = [False]
    core.Testing.test_pass_ = [0]
    core.Testing.test_fail_ = [0]

def test_message(message, verbose = False):
    if core.Testing.test_verbose_[-1] or verbose:
        print(core.ANSI.FG_YELLOW + '<T> ' + message + core.ANSI.FG_DEFAULT)

def test_stop(verbose = False):
    core.Testing.testing_[-1] = False
    core.Testing.test_pause_[-1] = False
    if core.Testing.test_f_[-1] is not None:
        eof_test = core.Testing.test_f_[-1].readline()
        if eof_test != '':
            test_message('The test was unexpectedly interrupted.', True)
            while eof_test != '':
                core.Testing.test_fail_[-1] += 1
                eof_test = core.Testing.test_f_[-1].readline()
        core.Testing.test_f_[-1].close()
    core.Testing.test_f_[-1] = None
    test_message('Test stopped.', verbose)
    testfile = core.Testing.test_filename_[-1]

    # if there is no testfile, we have no testing statistics
    if testfile is None or testfile == '':
        return

    # show testing statistics
    total = core.Testing.test_pass_[-1] + core.Testing.test_fail_[-1]
    s = 's' if total != 1 else ''
    tested = str(total) + ' line' + s + ' tested: '
    if core.Testing.test_pass_[-1] > 0:
        passed = core.ANSI.FG_GREEN + str(core.Testing.test_pass_[-1]) + ' passed' + core.ANSI.FG_YELLOW + ' :: '
    else:
        passed = str(core.Testing.test_pass_[-1]) + ' passed :: '
    if core.Testing.test_fail_[-1] > 0:
        failed = core.ANSI.FG_RED + str(core.Testing.test_fail_[-1]) + ' failed' + core.ANSI.FG_YELLOW + ' :: '
    else:
        failed = str(core.Testing.test_fail_[-1]) + ' failed :: '
    text_offset = 0 if total < 1000 else 2 # make room for big numbers
    test_message(rjustify(tested, 18 + text_offset) + rjustify(passed, 24 + text_offset) + failed + testfile, True)
    core.Testing.test_filename_[-1] = ''

def test_versions(ranges):
    # make sure a test is running
    if not core.Testing.test_filename_[-1]:
        test_message(f"&test versions {ranges}:", True)
        test_message('  Please start a test first.', True)
        test_stop()
        return

    # get the version and break it down
    version = core.Main.version_[1:].split('.')
    num_segments = len(version)
    matching = False

    # break down the ranges into space-separated entries
    entries = ranges.split(' ')

    # examine each entry
    for entry in entries:
        num_matching = 0

        # the initial v is optional
        if entry.startswith('v'):
            entry = entry[1:]

        # skip if the user types two spaces in a row
        if entry == '':
            continue

        # break down the entry into dot-separated segments
        segments = entry.split('.')

        # fail this entry if we find the wrong number of segments
        if len(segments) != num_segments:
            continue

        # examine each segment
        for j, segment in enumerate(segments):

            # wildcard
            if entry == '*' or version[j] == segment:
                num_matching = num_matching + 1

            # numerical ranges
            else:
                if '-' in segment:
                    dashes = segment.split('-')
                    first = int(dashes[0])
                    last = int(dashes[1])
                    if int(version[j]) >= first and int(version[j]) <= last:
                        num_matching = num_matching + 1
                elif '+' in segment:
                    dashes = segment.split('+')
                    first = int(dashes[0])
                    if int(version[j]) >= first:
                        num_matching = num_matching + 1

            # it matches!
            if num_matching == num_segments:
                matching = True
                break

    # if we do not find a match, stop the test
    if not matching:
        this_version = core.Main.version_
        if this_version.startswith('v'):
            this_version = this_version[1:]
        test_message(f"This test was not designed for version {this_version}. Expected: {ranges}", True)
        core.Testing.test_filename_[-1] = None
        test_stop()

def list_vars_(class_obj, filters, fullname = False, classname = None):
    # 'testing' is the longest built-in class name
    class_width = 7

    # 'line_parse_delimiter' is usually the longest variable name
    var_width = 21

    if classname is None:
        classname = class_obj.__name__
    if fullname:
        classname = f"{class_obj.__module__}.{class_obj.__name__}"

        # 'core.Testing' is the longest built-in full class name
        class_width = 12

        # the plugin class full name tends to be the longest
        plugin_classname = f"{bridge.Plugin.my.__module__}.{bridge.Plugin.my.__name__}"
        if len(plugin_classname) > len(classname):
            class_width = len(plugin_classname)

    class_vars = vars(class_obj)

    # check for partial matches
    partial_matches = []
    for testing_filter in filters:
        p = [cv for cv in class_vars if testing_filter in cv]
        partial_matches.extend(p)
    filters.extend(partial_matches)

    # check for class or variable matches
    for var in class_vars:
        attr = getattr(class_obj, var)

        # we only want our own variables
        if not var.startswith('__') and not callable(attr):

            # finally check for matches
            if filters == [] or var in filters or classname in filters:

                # prettier name
                if var.endswith('_') and not fullname:
                    var = var[:-1]

                # passed the filters
                print(f"{classname.rjust(class_width)}.{var.ljust(var_width)} = {attr}")

def debug(argv, fullname = False):
    if argv is not None:
        filters = argv.split()
    else:
        filters = []
    list_vars_(core.Main, filters, fullname)
    list_vars_(core.Cli, filters, fullname)
    list_vars_(core.Testing, filters, fullname)
    list_vars_(bridge.Plugin.my, filters, fullname, 'plugin')
