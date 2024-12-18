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
import core_functions
import var_functions

# abstraction layer for plugins
import bridge

core.Main.version_ = 'v0.0.38'

################################################################################
# send data to the plugin for processing
################################################################################

def process_data(cli_filenames): # pylint: disable=too-many-branches
    should_stop = True
    try:
        if core.Main.interactive_:
            prompt = core.Main.interactive_prompt_
            if core.Main.goto_[-1] is not None or core.Main.until_ is not None:
                prompt = core.Main.interactive_prompt_focused_
            line = input(prompt)
            if not core_functions.skip_line(line):
                line = var_functions.parse_references(line)
                bridge.Plugin.parse_line(line)
            var_functions.process_release()
            should_stop = False
        else:
            with fileinput.FileInput(files=(cli_filenames), mode='r') as lines:
                for line in lines:
                    line = re.sub('\n', '', line)
                    if not core_functions.skip_line(line):
                        line = var_functions.parse_references(line)
                        bridge.Plugin.parse_line(line)
                    var_functions.process_release()
                    if not core.Main.running_[-1]:
                        break
    except EOFError:
        print()
        should_stop = True
    except FileNotFoundError as e:
        core.Main.msg.error_message(f"Input file not found: {e.filename}")
    except IndexError:
        core.Main.msg.error_message(f"Badly formed data: {line}")
        should_stop = False
        if core.Cli.verbose_verbose_:
            traceback.print_exc()
    except ValueError:
        core.Main.msg.error_message(f"Invalid input: {line}")
        should_stop = False
        if core.Cli.verbose_verbose_:
            traceback.print_exc()
    except KeyboardInterrupt:
        core.Main.msg.error_message('Interrupted.')
    except: # pylint: disable=bare-except
        core.Main.msg.error_message('Unexpected error.')
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
filenames = core.Main.parser.parse_options()

# show information when starting in interactive mode
core.Main.interactive_ = core_functions.check_interactivity(filenames)
core_functions.show_info()

# main parsing loop
while core.Main.running_[-1]:
    process_data(filenames)
    if not core.Main.interactive_:
        break

# gracefully handle uncompleted goto directives
if core.Main.goto_[-1]:
    core.Main.msg.error_message(f"EOF reached before tag '{core.Main.goto_[-1]}")
