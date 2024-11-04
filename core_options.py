#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core functions to process options
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import sys

import core
import bridge
import core_functions

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
                    core_functions.use_plugin(plugin_name)
                    skip = True
                else:
                    core.Main.msg.error_message(f"Parameter expected: {option}")
                    core_functions.print_line()
                    core_functions.show_help('usage', True)
            elif option in ['-vv']:
                core.Cli.verbose_verbose_ = True
            elif option in ['-h', '---help']:
                topic = None
                if i < len(argv) - 1:
                    topic = argv[i+1]
                    skip = True
                core_functions.show_help(topic, True)
            elif option in ['-st', '--skip-testing']:
                core.Cli.skip_testing_ = True
            elif option in ['-tv', '--test-verbose']:
                core.Main.parser().parse_directive('&test verbose')
            elif option in ['-tfv', '--test-force-verbose']:
                core.Cli.test_force_verbose_ = True
                core.Main.parser().parse_directive('&test verbose')
            elif option in ['-tfq', '--test-force-quiet']:
                core.Cli.test_force_quiet_ = True
                core.Main.parser().parse_directive('&test quiet')
            else:
                if i < len(argv) - 1:
                    parameter = argv[i+1]
                else:
                    parameter = None
                # result[0] = known/unknown
                # result[1] = skip next word (option parameter)
                result = bridge.Plugin.parse_option(option, parameter)
                if not result[0]:
                    core.Main.msg.error_message(f"Unknown option: {option}")
                    core_functions.print_line()
                    core_functions.show_help('usage', True)
                else:
                    skip = result[1]
        elif i > 0:
            input_files.append(option)
    return input_files

def unrecognized_option(option):
    if option != '':
        core.Main.msg.error_message(f"Unrecognized option: {option}")

def no_options_recognized(options):
    for option in options:
        unrecognized_option(option)
