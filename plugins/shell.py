#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Shell plugin
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

from core_functions import Parser, is_directive, info_message

def identify():
    return 'shell'

class My():
    pass # placeholder
def get_env():
    pass # placeholder
def parse_option(option, parameter):
    return [False, False] # placeholder
def reset():
    pass # placeholder

def parse_my_directive(line):
    p = Parser()
    p.parse_directive(line)

def plugin_main(line):
    info_message(f"{identify()}: This plugin does not process data.")

def parse_line(line):
    if is_directive(line):
        parse_my_directive(line)
    else:
        plugin_main(line)
