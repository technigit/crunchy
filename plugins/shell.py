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

from core_directives import Parser, is_directive
from core_functions import info_message

def identify():
    return 'shell'

class My():
    pass # placeholder
def get_env():
    pass # placeholder
def parse_option(place = False, holder = False):
    return [place, holder]
def reset():
    pass # placeholder

def parse_line(line):
    if is_directive(line):
        Parser().parse_directive(line)
    else:
        info_message(f"{identify()}: This plugin does not process data.")
