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

# for interactive up/down arrow history
import readline # pylint: disable=unused-import

import core
from core_directives import parse_options
from core_functions import check_interactivity, show_info, skip_line, error_message
from var_functions import process_release

# abstraction layer for plugins
import bridge

core.Main.version_ = 'v0.0.35'

################################################################################
# send data to the plugin for processing
################################################################################

def process_data(cli_filenames): # pylint: disable=too-many-branches
    should_stop = True
    try:
        if core.Main.interactive_:
            line = input(core.Main.interactive_prompt_)
            if not skip_line(line):
                bridge.Plugin.parse_line(line)
            process_release()
            should_stop = False
        else:
            with fileinput.FileInput(files=(cli_filenames), mode='r') as lines:
                for line in lines:
                    line = re.sub('\n', '', line)
                    if not skip_line(line):
                        bridge.Plugin.parse_line(line)
                    process_release()
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
        if core.Cli.verbose_verbose_:
            traceback.print_exc()
    except ValueError:
        error_message(f"Invalid input: {line}")
        should_stop = False
        if core.Cli.verbose_verbose_:
            traceback.print_exc()
    except KeyboardInterrupt:
        error_message('Interrupted.')
    except: # pylint: disable=bare-except
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
