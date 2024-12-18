#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core functions to process directives
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import fileinput
import glob
import re
import traceback

import core
import bridge
import core_functions
import var_functions

################################################################################
# send data to the plugin for processing (from the &cli directive)
################################################################################

def process_data_from_directive(filenames):
    try:
        for filename in filenames:
            f = open(filename, 'r', encoding='utf-8')
            f_input = f.readlines()
            f.close()
            for line in f_input:
                line = re.sub('\n', '', line)
                if not core_functions.skip_line(line):
                    bridge.Plugin.parse_line(line)
    except FileNotFoundError as e:
        core.Main.msg.error_message(f"cli: Input file not found: {e.filename}")
    except IndexError:
        core.Main.msg.error_message(f"cli: Badly formed data: {line}")
    except ValueError:
        core.Main.msg.error_message(f"cli: Invalid input: {line}")
    except KeyboardInterrupt:
        core.Main.msg.error_message('Interrupted.')
    except: # pylint: disable=bare-except
        core.Main.msg.error_message('Unexpected error.')
        traceback.print_exc()
    finally:
        fileinput.close()

################################################################################
# core class to handle parsing
################################################################################

class DirectiveParser:
    # parser class to be set up as an object that can be used by plugins

    def __init__(self):
        self.arg = None
        self.argtrim = None
        self.cmd = None
        self.done = True
        self.line = None
        self.m = None
        self.options = None
        self.usage = None

    ########################################

    def is_directive(self, line):
        # check whether the input line is calling a directive

        return re.search(r'^\s*&', line)

    ########################################

    def parse_directive(self, line):
        # parse a directive from anywhere outside of the normal input stream
        # detect invalid usage or invalid directive

        self.pre_parse_directive(line)
        if not self.done:
            if self.usage:
                self.invalid_usage()
            else:
                self.line = line
                self.invalid_directive()

    ########################################

    def parse_setting(self, setting, arg):
        # standardized parsing of the &set directive
        # the calling function guarantees a value parameter

        # &set <setting> "<value>"
        m = re.search(r'^.*' + setting + r'\s\"(.*)\"$', arg)

        # &set <setting> '<value>'
        if m is None:
            m = re.search(r'^.*' + setting + r'\s\'(.*)\'$', arg)

        # &set <setting> <value>
        if m is None:
            m = re.search(r'^.*' + setting + r'\s(.*)$', arg)

        # return the value
        return m.group(1)

    ########################################

    def invalid_directive(self):
        # error message for unrecognized directives

        core.Main.msg.error_message(f"Invalid directive: {self.line}")

    ########################################

    def invalid_usage(self, plugin_usage = None):
        # handle invalid usage for general directives and plugin directives

        if self.usage is not None:
            general = 'General ' if self.usage is not None and plugin_usage is not None else ''
            core.Main.msg.error_message(f"{general}Usage: {self.usage}")
        if plugin_usage is not None:
            plugin = 'Plugin ' if self.usage is not None and plugin_usage is not None else ''
            core.Main.msg.error_message(f"{plugin}Usage: {plugin_usage}")

    ########################################

    def unrecognized_action(self, cmd, action):
        # handle unrecognized action for directives

        if action is not None:
            core.Main.msg.error_message(f"Unrecognized {cmd + ' ' if cmd is not None else ''}action: {action}")

    def no_actions_recognized(self, cmd, action):
        # handle unrecognized action for directives that have no actions

        self.unrecognized_action(cmd, action)

    ########################################

    def pre_parse_directive(self, line):
        # parse core directives (before plugins parse their own directives)

        self.line = line
        arg = None
        argtrim = None
        options = []
        m = re.search(r'^\s*\S(cli)\s(.*)$', line)
        if m is not None:
            arg = m.group(2)
            argtrim = arg.strip()
        else:
            m = re.search(r'^\s*\S(\S*)\s(.*)$', line)
            if m:
                arg = m.group(2)
                argtrim = arg.strip()
                while arg.startswith('-'):
                    options.append(argtrim.split()[0])
                    # trim the option and remove one space after it
                    arg = re.sub(r'^\s*' + options[-1], '', arg)
                    arg = re.sub(r'^\s', '', arg)
                    # trim the option and remove all spaces after it
                    argtrim = re.sub(r'^' + options[-1], '', argtrim)
                    argtrim = argtrim.lstrip()
                if len(options) == 0:
                    options.append('') # insert dummy element
            else:
                m = re.search(r'^\s*\S(\S*)$', line)
        cmd = m.group(1)
        action = None
        m = re.search(r'^([^\.]*)\.(.*)$', cmd)
        if m is not None:
            cmd = m.group(1)
            action = m.group(2)

        ####################

        if cmd == 'cd':
            self.no_actions_recognized(cmd, action)
            quiet = False
            for option in options:
                if option in ['-q', '--quiet']:
                    quiet = True
                else:
                    core.Main.parser.unrecognized_option(option)
            core.Main.read_path_[-1] = argtrim
            if core.Main.read_path_[-1] and not quiet:
                core.Main.msg.info_message(f"Setting current working directory to '{core.Main.read_path_[-1]}'.")
            elif not quiet:
                core.Main.msg.info_message('Resetting current working directory.')

        ####################

        elif cmd == 'cli':
            self.no_actions_recognized(cmd, action)
            if argtrim is None:
                # mimic command line result without any parameters
                core_functions.show_info(True)
            else:
                # insert placeholder
                cli_argv = '. ' + argtrim
                # run the options as if from the command line
                filenames = core.Main.parser.parse_options(cli_argv.split())
                process_data_from_directive(filenames)

        ####################

        elif cmd == 'goto':
            self.no_actions_recognized(cmd, action)
            quiet = False
            for option in options:
                if option in ['-q', '--quiet']:
                    quiet = True
                else:
                    core.Main.parser.unrecognized_option(option)
            core.Main.goto_[-1] = argtrim
            if argtrim and not quiet:
                core.Main.msg.info_message(f"Skipping to '{core.Main.goto_[-1]}'.")
            elif not quiet:
                self.invalid_usage('&goto <label>')

        ####################

        elif cmd == 'header':
            self.no_actions_recognized(cmd, action)
            if argtrim:
                core.Main.elements_ = core_functions.get_elements(argtrim)
                core.Main.headers_[-1] = core_functions.make_headers()
            if core.Main.headers_[-1]:
                core.Main.header_mode_ = True
                print_header = True
                for option in options:
                    if option in ['-q', '--quiet']:
                        print_header = False
                    else:
                        core.Main.parser.unrecognized_option(option)
                if print_header:
                    headers = '  '.join(core.Main.headers_[-1])
                    if not bridge.Plugin.identify() in core.Main.does_not_process_data:
                        # this plugin processes data
                        bridge.Plugin.parse_line(headers)
                    else:
                        # this plugin does not process data
                        # plugins/shell.py is an example
                        out = core_functions.pre_parse(headers)
                        if core.Main.output_[-1] and out is not None:
                            core_functions.print_line(out)
            else:
                core.Main.msg.error_message('No header information found.')

        ####################

        elif cmd == 'help':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            core_functions.show_help(argtrim)

        ####################

        elif cmd == 'identify':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            core.Main.msg.info_message(f"Loaded plugin: {bridge.Plugin.identify()}")

        ####################

        elif cmd == 'map':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            show_usage = False
            if argtrim:
                premap = core_functions.get_elements(argtrim)
                core.Main.map_[-1] = [None] * len(premap)
                try:
                    for m, element in enumerate(premap):
                        core.Main.map_[-1][int(premap[m]) - 1] = m + 1
                    core.Main.msg.info_message('Fields were remapped.')
                except ValueError:
                    show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.invalid_usage('&map <int><space><space><int>...')

        ####################

        elif cmd == 'output' and arg == 'on':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            core.Main.output_[-1] = True
            core.Main.msg.info_message('Output mode is on.')
        elif cmd == 'output' and arg == 'off':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            core.Main.msg.info_message('Output mode is off.')
            core.Main.output_[-1] = False
        elif cmd == 'output':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            self.invalid_usage('&output on|off')

        ####################

        elif cmd == 'print':
            self.no_actions_recognized(cmd, action)
            self.done = False
            if argtrim and argtrim.startswith('"'):
                # leading double quote
                argtrim = argtrim[1:]
                arg = argtrim
                if argtrim.endswith('"'):
                    # optional matching double quote
                    argtrim = argtrim[:-1]
                    arg = argtrim
            for option in options:
                if option in ['-f', '--force']:
                    # force print
                    core_functions.print_line(arg)
                    self.done = True
                else:
                    core.Main.parser.unrecognized_option(option)
            if not self.done:
                if core.Main.output_[-1]:
                    if arg is not None:
                        core_functions.print_line(arg)
                    else:
                        core_functions.print_line()
                else:
                    pass
            self.done = True

        ####################

        elif cmd == 'read':
            self.no_actions_recognized(cmd, action)
            if argtrim:
                quiet_mode = False
                for option in options:
                    if option in ['-i', '--inline']:
                        core.Main.read_inline_ = True
                    elif option in ['-s', '--sandbox']:
                        core.Main.read_inline_ = False
                    elif option in ['-q', '--quiet']:
                        quiet_mode = True
                    else:
                        core.Main.parser.unrecognized_option(option)
                read_source = argtrim
                read_sources = read_source.split(' ')
                s = 's' if len(read_sources) > 1 else ''
                inline = ' (inline mode)' if core.Main.read_inline_ else ''
                if core.Main.read_path_[-1]:
                    for i, rs in enumerate(read_sources):
                        read_sources[i] = core.Main.read_path_[-1] + '/' + rs
                if core.Main.max_read_depth_ > 0:
                    core.Main.max_read_depth_ = core.Main.max_read_depth_ - 1
                    if not quiet_mode:
                        core.Main.msg.info_message(f"Reading file{s}: {read_source}{inline}")
                    core_functions.push_env()
                    try:
                        with fileinput.FileInput(files=(read_sources), mode='r') as read_lines:
                            for read_line in read_lines:
                                read_line = re.sub('\n', '', read_line)
                                if not core_functions.skip_line(read_line):
                                    bridge.Plugin.parse_line(read_line)
                                var_functions.process_release()
                                if not core.Main.running_[-1]:
                                    break
                    except FileNotFoundError as e:
                        core.Main.msg.error_message(f"{cmd}: Input file not found: {e.filename}")
                    except IndexError:
                        core.Main.msg.error_message(f"{cmd}: Badly formed data: {read_line}", True)
                    except ValueError:
                        core.Main.msg.error_message(f"{cmd}: Invalid input: {read_line}", True)
                    except: # pylint: disable=bare-except
                        core.Main.msg.error_message(f"{cmd}: Unexpected error.", True)
                        traceback.print_exc()
                    finally:
                        if core.Testing.testing_[-1]:
                            core.Testing.testStop()
                        core_functions.pop_env()
                        if not quiet_mode:
                            core.Main.msg.info_message(f"Finished reading file{s}: {read_source}{inline}")
                    core.Main.max_read_depth_ = core.Main.max_read_depth_ + 1
                else:
                    core.Main.msg.error_message(f"{cmd}: Nested level too deep; will not read {read_source}.")
            else:
                self.invalid_usage('&read <filenames>')

        ####################

        elif cmd == 'set':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            show_usage = False
            if argtrim:
                parts = argtrim.split()
                if len(parts) > 1:
                    if parts[0] == 'currency':
                        core.Main.currency_format_ = self.parse_setting('currency', arg)
                    elif parts[0] == 'percentage':
                        core.Main.percentage_format_ = self.parse_setting('percentage', arg)
                    elif parts[0] == 'margin':
                        core.Main.margin_ = self.parse_setting('margin', arg)
                    elif parts[0] == 'prompt':
                        core.Main.interactive_prompt_ = self.parse_setting('prompt', arg)
                    else:
                        show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.done = False
                self.usage = '&set [ prompt <string> ]'

        ####################

        elif cmd == 'stop':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)

            # --ignore-stop: continue reading data and ignore the &stop directive
            # otherwise, stop testing and stop running
            if not core.Cli.ignore_stop_:
                if core.Testing.testing_[-1]:
                    core.Testing.testStop()
                core.Main.running_[-1] = False

            # --ignore-stop-reset: same as --ignore-stop, but also reset all running values
            if core.Cli.ignore_stop_reset_:
                if core.Testing.testing_[-1]:
                    core.Testing.testStop()
                core.reset()
                core.Testing.reset()
                bridge.Plugin.reset()

        ####################

        elif cmd == 'timer':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            if argtrim is not None:
                label = ''
                mode = None
                for element in argtrim.split():
                    if element in ['start', 'stop']:
                        mode = element
                    else:
                        label = element
                if mode == 'start':
                    core_functions.timer_start(label)
                elif mode == 'stop':
                    core_functions.timer_stop()
            else:
                core_functions.timer_status()

        ####################

        elif cmd == 'use':
            self.no_actions_recognized(cmd, action)
            if argtrim is not None:
                quiet = False
                for option in options:
                    if option in ['-q']:
                        quiet = True
                    else:
                        core.Main.parser.unrecognized_option(option)
                core.reset(False)
                core_functions.use_plugin(argtrim)
                if not quiet:
                    DirectiveParser().parse_directive('&identify')
            else:
                DirectiveParser().parse_directive('&identify')
                plugins = glob.glob(core.Main.source_path_ + '/plugins/*.py')
                plugins.sort()
                other_plugins = ''
                current_plugin = bridge.Plugin.identify()
                for plugin in plugins:
                    m = re.search(r'^.*\/([\S\s]*).py', plugin)
                    name = m.group(1)
                    if name != current_plugin:
                        other_plugins += name + '  '
                core.Main.msg.info_message(f"Also available:  {other_plugins.strip()}")

        ####################

        elif cmd == 'var':
            core.Main.until_quiet_ = False
            if action is not None:
                if not var_functions.var_action(action, argtrim, options):
                    self.unrecognized_action(cmd, action)
            if argtrim is not None and action is None:
                m = re.search(r'^(.*)\s(-+[-\sa-zA-Z0-9]*)$', argtrim)
                if m is not None:
                    options += m.group(2).split()
                    argtrim = m.group(1)
                parts = argtrim.split()
                var_key = parts[0]
                var_values = []
                m = re.search(r'^[^\s]+\s+(.*)$', argtrim)
                if m is not None:
                    var_values = var_functions.get_values(m.group(1))
                if var_values is not None:
                    has_var_values = len(var_values) >= 1
                else:
                    has_var_values = False
                should_set_var = True
                should_show_var_only = True
                should_defer_show = False
                append = False
                skip = False
                for i, option in enumerate(options):
                    if skip:
                        skip = False
                        continue
                    if option in ['-A', '--append'] and has_var_values:
                        var_functions.push_var(var_key, var_values)
                        should_set_var = False
                    elif option in ['-A', '--append'] and not has_var_values:
                        append = True
                    elif option in ['-D', '--duplicate']:
                        var_functions.dup_var(var_key, var_values)
                        should_set_var = False
                        should_show_var_only = False
                    elif option in ['-p', '--pop']:
                        var_functions.pop_var(var_key)
                    elif option in ['-q', '--quiet']:
                        core.Main.until_quiet_ = True
                    elif option in ['--until']:
                        if not append:
                            var_functions.del_var([var_key])
                        should_set_var = False
                        should_defer_show = True
                        skip = True
                        core.Main.until_ = options[i+1]
                        core.Main.until_var_key_ = var_key
                        core.Main.parser.freeze_history()
                    elif option in ['-x', '--delete']:
                        var_functions.del_var([var_key] + var_values)
                        should_set_var = False
                        should_show_var_only = False
                if should_set_var and has_var_values:
                    var_functions.set_var(var_key, var_values)
                if should_show_var_only and not should_defer_show:
                    core.Main.msg.info_message(var_functions.show_var(var_key))
                elif not should_defer_show:
                    for key in [var_key] + var_values:
                        core.Main.msg.info_message(var_functions.show_var(key))
            elif action is None:
                core.Main.msg.info_message(var_functions.show_all_vars())

        ####################

        elif cmd == 'test' and core.Cli.skip_testing_:
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
        elif cmd == 'test':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            if argtrim is None:
                core.Testing.testMessage(f"Usage: &{cmd} <parameters>")
            elif argtrim.startswith('start '):
                if not core.Testing.testing_[-1]:
                    m = re.search(r'^start\s+(\S*)$', argtrim)
                    if m:
                        core.Testing.test_filename_[-1] = m.group(1)
                        core.Testing.testing_[-1] = True
                        core.Testing.test_pause_[-1] = False
                        core.Testing.test_pass_[-1] = 0
                        core.Testing.test_fail_[-1] = 0
                        core.Testing.testMessage(f"Test started with {core.Testing.test_filename_[-1]}")
                    else:
                        core.Testing.testMessage('Test filename not specified.')
                else:
                    core.Testing.testMessage(f"Test is already running ({core.Testing.test_filename_[-1]}).")
            elif argtrim == 'pause':
                if core.Testing.testing_[-1]:
                    core.Testing.test_pause_[-1] = True
                    core.Testing.testMessage('Test paused.')
                else:
                    core.Testing.testMessage('No test is currently running.')
            elif argtrim == 'resume':
                if core.Testing.testing_[-1]:
                    core.Testing.test_pause_[-1] = False
                    core.Testing.testMessage('Test resumed.')
                else:
                    core.Testing.testMessage('No test is currently running.')
            elif argtrim == 'verbose':
                if not core.Cli.test_force_quiet_:
                    core.Testing.test_verbose_[-1] = True
                    core.Testing.testMessage('Test mode set to verbose.')
            elif argtrim.startswith('versions '):
                m = re.search(r'^versions\s+(.*)$', argtrim)
                if m:
                    version_range = m.group(1)
                    core.Testing.testVersions(version_range)
                else:
                    core.Testing.testMessage('Version range not specified.')
            elif argtrim == 'quiet':
                if not core.Cli.test_force_verbose_:
                    core.Testing.test_verbose_[-1] = False
                    core.Testing.testMessage('Test mode set to quiet.')
            elif argtrim == 'stop':
                core.Testing.testStop()
            else:
                core.Testing.testMessage(f"{cmd}: invalid parameter(s) '{argtrim}'")


        ####################

        elif cmd == 'env':
            self.no_actions_recognized(cmd, action)
            core.Main.parser.no_options_recognized(options)
            if argtrim == 'push':
                core_functions.push_env()
            elif argtrim == 'pop':
                core_functions.pop_env()

        ####################

        elif cmd == 'debug':
            self.no_actions_recognized(cmd, action)
            fullname = False
            for option in options:
                if option in ['-fn', '--full-name']:
                    fullname = True
                else:
                    core.Main.parser.unrecognized_option(option)
            core.Testing.debug(argtrim, fullname)

        ####################

        elif cmd == 'infomsg' and arg == 'on':
            self.no_actions_recognized(cmd, action)
            quiet = False
            for option in options:
                if option in ['-q']:
                    quiet = True
                else:
                    core.Main.parser.unrecognized_option(option)
            core.Main.infomsg_[-1] = True
            if not quiet:
                core.Main.msg.info_message('Infomsg mode is on.')
        elif cmd == 'infomsg' and arg == 'off':
            self.no_actions_recognized(cmd, action)
            core.Main.infomsg_[-1] = False

        ####################

        else:
            self.done = False

        self.arg = arg
        self.argtrim = argtrim
        self.cmd = cmd
        self.m = m
        self.options = options
