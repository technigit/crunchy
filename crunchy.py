#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Main processing module
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import fileinput
import re
import traceback

import core
from core_functions import check_interactivity, show_info, parse_options, skip_line, error_message

# abstraction layer for plugins
import bridge

core.Main.version_ = 'v0.0.29'

################################################################################
# send data to the plugin for processing
################################################################################

def process_data(cli_filenames):
    should_stop = True
    try:
        if core.Main.interactive_:
            line = input(core.Main.interactive_prompt_)
            if not skip_line(line):
                bridge.Plugin.parseLine(line)
            should_stop = False
        else:
            with fileinput.FileInput(files=(cli_filenames), mode='r') as lines:
                for line in lines:
                    line = re.sub('\n', '', line)
                    if not skip_line(line):
                        bridge.Plugin.parseLine(line)
                    if not core.Main.running_[-1]:
                        break
    except EOFError:
        print()
        should_stop = True
    except FileNotFoundError as e:
        error_message(f"Input file not found: {e.filename}")
    except IndexError:
        error_message(f"Badly formed data: {line}")
        should_stop = False
    except ValueError:
        error_message(f"Invalid input: {line}")
        should_stop = False
    except KeyboardInterrupt:
        error_message('Interrupted.')
    except:
        error_message('Unexpected error.')
        traceback.print_exc()
    finally:
        if core.Testing.testing_[-1]:
            core.Testing.testStop()
    if should_stop:
        core.Main.running_[-1] = False

####################
# start here
####################

# initialize all environments
core.reset()
core.Testing.reset()
bridge.use_plugin('shell')

# process command-line options
filenames = parse_options()

# show information when starting in interactive mode
core.Main.interactive_ = check_interactivity(filenames)
show_info()

# main parsing loop
while core.Main.running_[-1]:
    process_data(filenames)
    if not core.Main.interactive_:
        break

# gracefully handle uncompleted goto directives
if core.Main.goto_[-1]:
    error_message(f"EOF reached before tag '{core.Main.goto_[-1]}")
