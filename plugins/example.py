#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Example plugin
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import core
from core_functions import pre_parse, map_elements, print_line

def identify():
    return 'example'

class My():
    sums_ = []
    rows_ = None

def reset():
    My.sums_ = [[]]
    My.rows_ = 0

class Cli():
    example_option = True

reset()

def get_env():
    return [
        My.sums_
    ]

################################################################################
# parse plugin-specific directives, but pre-parse for core directives first
################################################################################

def parse_my_directive(line):
    p = core.Main.parser()
    p.pre_parse_directive(line)
    if p.done:
        return
    argtrim = p.argtrim
    cmd = p.cmd

    ####################

    if cmd == 'example':
        if argtrim:
            core.Main.msg.info_message(f"This is an example directive output acting on '{argtrim}'")
        else:
            p.invalid_usage('&example <text>')

    elif cmd == 'stats':
        if argtrim:
            if argtrim == 'sums':
                if core.Main.output_[-1]:
                    print_line(map_elements(My.sums_[-1]))
            elif argtrim == 'averages':
                averages = []
                for avg_sum in My.sums_[-1]:
                    averages.append(f"{avg_sum/My.rows_:8.3f}")
                if core.Main.output_[-1]:
                    print_line(map_elements(averages))
        else:
            p.invalid_usage('&stats <type>')

    ####################

    else:
        p.invalid_directive()

################################################################################
# add command-line options just for this plugin
################################################################################

def parse_option(option, parameter):
    # result[0] = known/unknown
    # result[1] = skip next word (option parameter)
    result = [False, False]
    if parameter is None:
        parameter = ''
    if option in ['-eo', '--example-option']:
        core.Main.msg.info_message('This is an example option output with no parameters.')
        result = [True, False]
    elif option in ['-eop', '--example-option-parameter']:
        core.Main.msg.info_message(f"This is an example option output with a parameter: {parameter}")
        result = [True, True]
    return result

################################################################################
# plugin-specific parsing
################################################################################

def plugin_main(line):
    out = pre_parse(line)
    if core.Main.header_mode_:
        if core.Main.output_[-1] and out is not None:
            print_line(out)
        core.Main.header_mode_ = False
        return
    linesum = 0
    for i, element in enumerate(core.Main.elements_):
        if len(My.sums_[-1]) >= i + 1:
            My.sums_[-1][i] += int(element)
        else:
            My.sums_[-1].append(int(element))
        linesum += int(element)
    if core.Main.output_[-1]:
        print_line(f"{out} {linesum:8.0f} {linesum / len(core.Main.elements_):8.3f}")
    My.rows_ += 1

####################
# start here
####################

def parse_line(line):
    if core.Main.parser().is_directive(line):
        parse_my_directive(line)
    else:
        plugin_main(line)
