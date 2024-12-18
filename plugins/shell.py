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

import core

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
    if core.Main.parser().is_directive(line):
        core.Main.parser().parse_directive(line)
    else:
        core.Main.msg.info_message(f"{identify()}: This plugin does not process data, except via directives.")
