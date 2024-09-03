#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Core Functions
#
################################################################################

import fileinput, glob, re, sys, textwrap, time, traceback
from os.path import dirname, exists, realpath

import core, bridge

################################################################################
# show utility information in interactive mode
################################################################################

def showInfo(should_show = False):
    if should_show or core.main.interactive_:
        printLine("""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
{0}

To get help, enter &help
To exit interactive mode, use Ctrl-D
""".format(core.main.version_))

def checkInteractivity(filenames):
    if filenames == None or filenames == []:
        interactive = sys.stdin.isatty()
    else:
        interactive = False
    return interactive

################################################################################
# text formatting
################################################################################

def formatElement(index, elements):
    element = elements[index]
    return formatElementByValue(index, element)

def formatElementByValue(index, element):
    padding = ' '
    if isFloat(element) and not isInteger(element):
        formats = core.main.formats_[-1][index]
        if not core.main.header_mode_:
            padding = core.main.padding_[-1][index]
        if formats != None:
            if '~' in formats:
                element = str(round(float(element)))
            if '$' in formats:
                element = currency(float(element))
            elif '%' in formats:
                element = percentage(float(element))
    elif element.strip() != '' and not core.main.header_mode_:
        padding = core.main.padding_[-1][index]
    align = core.main.justify_[-1][index]
    if align == '<':
        return ljustify(str(element), core.main.width_[-1][index], padding) + core.main.margin_
    if align == '|' or align == '^':
        return cjustify(str(element), core.main.width_[-1][index], padding) + core.main.margin_
    if align == '>':
        return rjustify(str(element), core.main.width_[-1][index], padding) + core.main.margin_

def ljustify(str, width, padding = ' '):
    return str.ljust(width, padding)[:width]

def cjustify(str, width, padding = ' '):
    return str.center(width, padding)[:width]

def rjustify(str, width, padding = ' '):
    return str.rjust(width, padding)[:width]

def currency(num):
    try:
        return core.main.currency_format_.format(num)
    except:
        if core.cli.verbose_verbose_:
            errorMessage(f"Currency error: {num}, {core.main.currency_format_}")
            traceback.print_exc()
            core.main.running_[-1] = False
            popEnv()
        return 'ERROR'

def percentage(num):
    try:
        return core.main.percentage_format_.format(num)
    except:
        if core.cli.verbose_verbose_:
            errorMessage(f"Percentage error: {num}, {core.main.percentage_format_}")
            traceback.print_exc()
            core.main.running_[-1] = False
            popEnv()
        return 'ERROR'

def isInteger(num):
    try:
        intnum = int(num)
        return intnum == num
    except:
        return False

def isFloat(num):
    try:
        float(num)
        return True
    except:
        return False

################################################################################
# timer
################################################################################

def timerGetLabel():
    if core.main.timer_label_[-1].isdigit():
        return core.main.timer_label_[-1]
    else:
        return f"'{core.main.timer_label_[-1]}'"

def timerPutLabel(label):
    if label == '':
        label = str(len(core.main.timer_) - 1)
    core.main.timer_label_[-1] = label

def timerStart(label = ''):
    timerPutLabel(label)
    if core.main.timer_[-1]:
        infoMessage('Timer {0} is already running.'.format(timerGetLabel()))
    else:
        core.main.timer_[-1] = True
        core.main.timer_ts_[-1] = time.time()
        infoMessage('Timer {0} started.'.format(timerGetLabel()))

def timerStop():
    if not core.main.timer_[-1]:
        infoMessage('Timer {0} is not running.'.format(timerGetLabel()))
    else:
        core.main.timer_[-1] = False
        ts = time.time()
        infoMessage('Timer {0} stopped, {1} elapsed.'.format(timerGetLabel(), timerElapsed(core.main.timer_ts_[-1], ts)))

def timerStatus():
    if core.main.timer_[-1]:
        infoMessage('Timer {0} is running.'.format(timerGetLabel()))
    else:
        infoMessage('Timer {0} is not running.'.format(timerGetLabel()))

def timerElapsed(start, stop):
    return '{:.5f}s'.format(stop - start)

################################################################################
# process data
#
#    - Data elements are delimited by two spaces.
#    - A dash denotes an empty data element.
################################################################################

def getElements(line):
    # non-printable null character for internal parsing
    delim = '\x00'

    # convert the delimiter into delim and split the line into elements
    # this approach allows multi-character delimiters
    line = re.sub(core.main.line_parse_delimiter_, delim, line.lstrip())
    core.main.elements_ = line.split(delim)

    # dashes are placeholders for empty fields
    for i, element in enumerate(core.main.elements_):
        if element == core.main.line_element_placeholder_:
            core.main.elements_[i] = ' '

    # now we have the elements to send back
    return core.main.elements_

################################################################################
# generate header data according to specifications
################################################################################

def makeHeaders():
    # initialize header attributes
    core.main.formats_[-1] = [None] * len(core.main.elements_)
    core.main.justify_[-1] = [None] * len(core.main.elements_)
    core.main.padding_[-1] = [None] * len(core.main.elements_)
    core.main.width_[-1] = [None] * len(core.main.elements_)

    # iterate over header specification
    for i, element in enumerate(core.main.elements_):

        # prepare the element for clean parsing
        element = element.strip()

        # parse the header element specification
        m = re.search('^(#?)([~$%]*)(.*[a-zA-Z])([<|^>]?)(\d+)(\D?)$', element)

        # valid format
        if m != None:

            # extract specification parameters
            m_comment = m.group(1)
            m_formats = m.group(2)
            m_heading = m.group(3)
            m_justify = m.group(4)
            m_width = m.group(5)
            m_padding = m.group(6)
            if m_justify == '': m_justify = '>'
            if m_padding == '': m_padding = ' '

            # store specification parameters
            core.main.elements_[i] = m_comment + m_heading
            core.main.formats_[-1][i] = m_formats
            core.main.justify_[-1][i] = m_justify
            core.main.width_[-1][i] = int(m_width)
            core.main.padding_[-1][i] = m_padding

        # invalid format
        else:
            return None

    # return extracted headers
    return core.main.elements_

################################################################################
# process headers
#
#    - Stores elements in core.main.elements_ for internal processing.
#    - Returns a mapped set of elements if there is an output.
#    - Returns None if there is no output.
################################################################################

def preParse(line):
    # break the line down into its constituent parts
    core.main.elements_ = getElements(line)

    # current plugin not using headers: done, no mapping needed
    if not core.main.using_headers_:
        return

    # if we don't have a header yet, then we need to get one now
    if core.main.headers_[-1] == None:
        core.main.headers_[-1] = makeHeaders()
        core.main.header_mode_ = True

    # if we still don't have a header at this point, then the data is misconfigured
    if core.main.headers_[-1] == None:
        errorMessage(f"Invalid header configuration: {line}")
        if not core.main.interactive_:
            core.main.running_[-1] = False
            popEnv()
        return

    # return the header or data elements, after mapping
    return mapElements(core.main.elements_)

################################################################################
# map header/data elements to rearrange "columns" according to specifications
################################################################################

def mapElements(elements):
    out = ''
    for i, element in enumerate(elements):
        m = i
        if core.main.map_[-1] != None:
            m = core.main.map_[-1][i] - 1
        if not core.main.headers_[-1][m].startswith('#'):
            out += formatElement(m, elements)
    return out

################################################################################
# parse primary directives
################################################################################

def isDirective(line):
    return re.search('^\s*&', line)

class Parser:
    # parser class to be set up as an object that can be used by plugins

    def __init__(self):
        self.done = True
        self.usage = None

    def parseDirective(self, line):
        self.preParseDirective(line)
        if not self.done:
            if self.usage:
                self.invalidUsage()
            else:
                self.line = line
                self.invalidDirective()

    def parseSetting(self, setting, arg):
        # standardized parsing of the &set directive
        # the calling function guarantees a value parameter

        # &set <setting> "<value>"
        m = re.search('^.*' + setting + '\s\"(.*)\"$', arg)

        # &set <setting> '<value>'
        if m == None:
            m = re.search('^.*' + setting + '\s\'(.*)\'$', arg)

        # &set <setting> <value>
        if m == None:
            m = re.search('^.*' + setting + '\s(.*)$', arg)

        # return the value
        return m.group(1)

    def invalidDirective(self):
        errorMessage(f"Invalid directive: {self.line}")

    def invalidUsage(self, plugin_usage = None):
        if self.usage != None:
            general = 'General ' if self.usage != None and plugin_usage != None else ''
            errorMessage(f"{general}Usage: {self.usage}")
        if plugin_usage != None:
            plugin = 'Plugin ' if self.usage != None and plugin_usage != None else ''
            errorMessage(f"{plugin}Usage: {plugin_usage}")

    def preParseDirective(self, line):
        self.line = line
        arg = None
        argtrim = None
        options = []
        m = re.search('^\s*\S(cli)\s(.*)$', line)
        if m:
            arg = m.group(2)
            argtrim = arg.strip()
        else:
            m = re.search('^\s*\S(\S*)\s(.*)$', line)
            if m:
                arg = m.group(2)
                argtrim = arg.strip()
                while arg.startswith('-'):
                    options.append(argtrim.split()[0])
                    # trim the option and remove one space after it
                    arg = re.sub('^\s*' + options[-1], '', arg)
                    arg = re.sub('^\s', '', arg)
                    # trim the option and remove all spaces after it
                    argtrim = re.sub('^' + options[-1], '', argtrim)
                    argtrim = argtrim.lstrip()
                if len(options) == 0:
                    options.append('') # insert dummy element
            else:
                m = re.search('^\s*\S(\S*)$', line)
        cmd = m.group(1)

        ####################

        if cmd == 'cd':
            noOptionsRecognized(options)
            core.main.read_path_[-1] = argtrim
            if core.main.read_path_[-1]:
                infoMessage("Setting current working directory to '{0}'.".format(core.main.read_path_[-1]))
            else:
                infoMessage('Resetting current working directory.')

        ####################

        elif cmd == 'cli':
            if argtrim == None:
                # mimic command line result without any parameters
                showInfo(True)
            else:
                # insert placeholder
                cli_argv = '. ' + argtrim
                # run the options as if from the command line
                filenames = parseOptions(cli_argv.split())
                processDataFromDirective(filenames)

        ####################

        elif cmd == 'goto':
            noOptionsRecognized(options)
            core.main.goto_[-1] = argtrim
            if argtrim:
                infoMessage("Skipping to '{0}'.".format(core.main.goto_[-1]))
            else:
                self.invalidUsage('&goto <label>')

        ####################

        elif cmd == 'header':
            if argtrim:
                core.main.elements_ = getElements(argtrim)
                core.main.headers_[-1] = makeHeaders()
            if core.main.headers_[-1]:
                core.main.header_mode_ = True
                print_header = True
                for option in options:
                    if option in ['-q', '--quiet']:
                        print_header = False
                    else:
                        unrecognizedOption(option)
                if print_header:
                    bridge.plugin.parseLine('  '.join(core.main.headers_[-1]))
            else:
                errorMessage('No header information found.')

        ####################

        elif cmd == 'help':
            noOptionsRecognized(options)
            showHelp(argtrim)

        ####################

        elif cmd == 'identify':
            noOptionsRecognized(options)
            infoMessage('Loaded plugin: {0}'.format(bridge.plugin.identify()))

        ####################

        elif cmd == 'map':
            noOptionsRecognized(options)
            show_usage = False
            if argtrim:
                premap = getElements(argtrim)
                core.main.map_[-1] = [None] * len(premap)
                try:
                    for m, element in enumerate(premap):
                        core.main.map_[-1][int(premap[m]) - 1] = m + 1
                    infoMessage('Fields were remapped.')
                except ValueError:
                    show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.invalidUsage('&map <int><space><space><int>...')

        ####################

        elif cmd == 'output' and arg == 'on':
            noOptionsRecognized(options)
            core.main.output_[-1] = True
            infoMessage('Output mode is on.')
        elif cmd == 'output' and arg == 'off':
            noOptionsRecognized(options)
            infoMessage('Output mode is off.')
            core.main.output_[-1] = False
        elif cmd == 'output':
            noOptionsRecognized(options)
            self.invalidUsage('&output on|off')

        ####################

        elif cmd == 'print':
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
                    printLine(arg)
                    self.done = True
                else:
                    unrecognizedOption(option)
            if not self.done:
                if core.main.output_[-1]:
                    printLine(arg) if arg is not None else printLine()
                else:
                    pass
            self.done = True

        ####################

        elif cmd == 'read':
            if argtrim:
                for option in options:
                    if option in ['-i', '--inline']:
                        core.main.read_inline_ = True
                    elif option in ['-s', '--sandbox']:
                        core.main.read_inline_ = False
                    else:
                        unrecognizedOption(option)
                read_source = argtrim
                read_sources = read_source.split(' ')
                s = 's' if len(read_sources) > 1 else ''
                inline = ' (inline mode)' if core.main.read_inline_ else ''
                if core.main.read_path_[-1]:
                    for i, rs in enumerate(read_sources):
                        read_sources[i] = core.main.read_path_[-1] + '/' + rs
                if core.main.max_read_depth_ > 0:
                    core.main.max_read_depth_ = core.main.max_read_depth_ - 1
                    infoMessage(f"Reading file{s}: {read_source}{inline}")
                    pushEnv()
                    try:
                        with fileinput.FileInput(files=(read_sources), mode='r') as read_lines:
                            for read_line in read_lines:
                                read_line = re.sub('\n', '', read_line)
                                if not skipLine(read_line): bridge.plugin.parseLine(read_line)
                                if not core.main.running_[-1]: break
                    except FileNotFoundError as e:
                        errorMessage(f"{cmd}: Input file not found: {e.filename}")
                    except IndexError:
                        errorMessage(f"{cmd}: Badly formed data: {read_line}", True)
                    except ValueError:
                        errorMessage(f"{cmd}: Invalid input: {read_line}", True)
                    except:
                        errorMessage(f"{cmd}: Unexpected error.", True)
                        traceback.print_exc()
                    finally:
                        if core.testing.testing_[-1]:
                            core.testing.testStop()
                        popEnv()
                        infoMessage(f"Finished reading file{s}: {read_source}{inline}")
                    core.main.max_read_depth_ = core.main.max_read_depth_ + 1
                else:
                    errorMessage(f"{cmd}: Nested level too deep; will not read {read_source}.")
            else:
                self.invalidUsage('&read <filenames>')

        ####################

        elif cmd == 'set':
            noOptionsRecognized(options)
            show_usage = False
            if argtrim:
                parts = argtrim.split()
                if len(parts) > 1:
                    if (parts[0] == 'currency'):
                        core.main.currency_format_ = self.parseSetting('currency', arg)
                    elif (parts[0] == 'percentage'):
                        core.main.percentage_format_ = self.parseSetting('percentage', arg)
                    elif (parts[0] == 'margin'):
                        core.main.margin_ = self.parseSetting('margin', arg)
                    elif (parts[0] == 'prompt'):
                        core.main.interactive_prompt_ = self.parseSetting('prompt', arg)
                    else:
                        show_usage = True
            else:
                show_usage = True
            if show_usage:
                self.done = False
                self.usage = '&set [ prompt <string> ]'

        ####################

        elif cmd == 'stop':
            noOptionsRecognized(options)

            # --ignore-stop: continue reading data and ignore the &stop directive
            # otherwise, stop testing and stop running
            if not core.cli.ignore_stop_:
                if core.testing.testing_[-1]:
                    core.testing.testStop()
                core.main.running_[-1] = False

            # --ignore-stop-reset: same as --ignore-stop, but also reset all running values
            if core.cli.ignore_stop_reset_:
                if core.testing.testing_[-1]:
                    core.testing.testStop()
                core.reset()
                core.testing.reset()
                bridge.plugin.reset()

        ####################

        elif cmd == 'timer':
            noOptionsRecognized(options)
            if argtrim != None:
                label = ''
                for element in argtrim.split():
                    if element in ['start', 'stop']:
                        mode = element
                    else:
                        label = element
                if mode == 'start':
                    timerStart(label)
                elif mode == 'stop':
                    timerStop()
            else:
                timerStatus()

        ####################

        elif cmd == 'use':
            if argtrim != None:
                quiet = False
                for option in options:
                    if option in ['-q']:
                        quiet = True
                    else:
                        unrecognizedOption(option)
                core.reset(False)
                usePlugin(argtrim)
                if not quiet:
                    parser.parseDirective('&identify')
            else:
                parser.parseDirective('&identify')
                plugins = glob.glob(core.main.source_path_ + '/plugins/*.py')
                plugins.sort()
                out = ''
                for plugin in plugins:
                    m = re.search('^.*\/([\S\s]*).py', plugin)
                    name = m.group(1)
                    if name != bridge.plugin.identify():
                        out += name + '  '
                infoMessage('Also available:  {0}'.format(out.strip()))

        ####################

        elif cmd == 'test' and core.cli.skip_testing_:
            noOptionsRecognized(options)
            pass
        elif cmd == 'test':
            noOptionsRecognized(options)
            if argtrim == None:
                core.testing.testMessage('Usage: &{0} <parameters>'.format(cmd))
            elif argtrim.startswith('start'):
                if not core.testing.testing_[-1]:
                    m = re.search('^start\s+(\S*)$', argtrim)
                    if m:
                        core.testing.test_filename_[-1] = m.group(1)
                        core.testing.testing_[-1] = True
                        core.testing.test_pause_[-1] = False
                        core.testing.test_pass_[-1] = 0
                        core.testing.test_fail_[-1] = 0
                        core.testing.testMessage("Test started with {0}".format(core.testing.test_filename_[-1]))
                    else:
                        core.testing.testMessage('Test filename not specified.')
                else:
                    core.testing.testMessage('Test is already running ({0}).'.format(core.testing.test_filename_[-1]))
            elif argtrim == 'pause':
                if core.testing.testing_[-1]:
                    core.testing.test_pause_[-1] = True
                    core.testing.testMessage('Test paused.')
                else:
                    core.testing.testMessage('No test is currently running.')
            elif argtrim == 'resume':
                if core.testing.testing_[-1]:
                    core.testing.test_pause_[-1] = False
                    core.testing.testMessage('Test resumed.')
                else:
                    core.testing.testMessage('No test is currently running.')
            elif argtrim == 'verbose':
                if not core.cli.test_force_quiet_:
                    core.testing.test_verbose_[-1] = True
                    core.testing.testMessage('Test mode set to verbose.')
            elif argtrim.startswith('versions'):
                m = re.search('^versions\s+(.*)$', argtrim)
                if m:
                    range = m.group(1)
                    core.testing.testVersions(range)
                else:
                    core.testing.testMessage('Version range not specified.')
            elif argtrim == 'quiet':
                if not core.cli.test_force_verbose_:
                    core.testing.test_verbose_[-1] = False
                    core.testing.testMessage('Test mode set to quiet.')
            elif argtrim == 'stop':
                core.testing.testStop()
            else:
                core.testing.testMessage('{0}: invalid parameter.'.format(cmd))

        ####################

        elif cmd == 'debug':
            fullname = False
            for option in options:
                if option in ['-fn', '--full-name']:
                    fullname = True
                else:
                    unrecognizedOption(option)
            core.testing.debug(argtrim, fullname)

        ####################

        elif cmd == 'infomsg' and arg == 'on':
            quiet = False
            for option in options:
                if option in ['-q']:
                    quiet = True
                else:
                    unrecognizedOption(option)
            core.main.infomsg_[-1] = True
            if not quiet:
                infoMessage('Infomsg mode is on.')
        elif cmd == 'infomsg' and arg == 'off':
            core.main.infomsg_[-1] = False

        ####################

        else:
            self.done = False

        self.arg = arg
        self.argtrim = argtrim
        self.cmd = cmd
        self.m = m
        self.options = options

################################################################################
# process command-line options
################################################################################

def parseOptions(argv = sys.argv):
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
                core.cli.ignore_stop_ = True
            elif option in ['-isr', '--ignore-stop-reset']:
                core.cli.ignore_stop_ = True
                core.cli.ignore_stop_reset_ = True
            elif option in ['-is0']: # undocumented, for testing purposes
                core.cli.ignore_stop_ = False
            elif option in ['-isr0']: # undocumented, for testing purposes
                core.cli.ignore_stop_ = False
                core.cli.ignore_stop_reset_ = False
            elif option in ['-up', '--use-plugin']:
                if i < len(argv) - 1:
                    plugin_name = argv[i+1]
                    usePlugin(plugin_name)
                    skip = True
                else:
                    errorMessage(f"Parameter expected: {option}")
                    printLine()
                    showHelp('usage', True)
            elif option in ['-vv']:
                core.cli.verbose_verbose_ = True
            elif option in ['-h', '---help']:
                topic = None
                if i < len(argv) - 1:
                    topic = argv[i+1]
                    skip = True
                showHelp(topic, True)
            elif option in ['-st', '--skip-testing']:
                core.cli.skip_testing_ = True
            elif option in ['-tv', '--test-verbose']:
                parser.parseDirective('&test verbose')
            elif option in ['-tfv', '--test-force-verbose']:
                core.cli.test_force_verbose_ = True
                parser.parseDirective('&test verbose')
            elif option in ['-tfq', '--test-force-quiet']:
                core.cli.test_force_quiet_ = True
                parser.parseDirective('&test quiet')
            else:
                if i < len(argv) - 1:
                    parameter = argv[i+1]
                else:
                    parameter = None
                # result[0] = known/unknown
                # result[1] = skip next word (option parameter)
                result = bridge.plugin.parseOption(option, parameter)
                if result[0] == False:
                    errorMessage(f"Unknown option: {option}")
                    printLine()
                    showHelp('usage', True)
                else:
                    skip = result[1]
        elif i > 0:
            input_files.append(option)
    return input_files

def unrecognizedOption(option):
    if option != '':
        errorMessage(f"Unrecognized option: {option}")

def noOptionsRecognized(options):
    for option in options:
        unrecognizedOption(option)

################################################################################
# send data to the plugin for processing (from the &cli directive)
################################################################################

def processDataFromDirective(filenames):
    try:
        for filename in filenames:
            f = open(filename, 'r')
            input = f.readlines()
            f.close()
            for line in input:
                line = re.sub('\n', '', line)
                if not skipLine(line): bridge.plugin.parseLine(line)
    except FileNotFoundError as e:
        errorMessage(f"cli: Input file not found: {e.filename}")
    except IndexError:
        errorMessage(f"cli: Badly formed data: {line}")
    except ValueError:
        errorMessage(f"cli: Invalid input: {line}")
    except KeyboardInterrupt:
        errorMessage('Interrupted.')
    except:
        errorMessage('Unexpected error.')
        traceback.print_exc()
    finally:
        fileinput.close()

################################################################################
# call usePlugin in the bridge module and catch errors
################################################################################

def usePlugin(plugin_name):
    try:
        bridge.usePlugin(plugin_name)
    except AttributeError:
        errorMessage(f"{plugin_name}: Incomplete plugin implementation.  Check that all attributes are implemented.", True)
    except ModuleNotFoundError:
        errorMessage(f"Plugin not found: {plugin_name}", True)

################################################################################
# send content to the output, but run it through testing if required
################################################################################

def printLine(line = '', stdio=sys.stdout):
    if core.testing.testing_[-1]:
        try:
            if core.testing.test_f_[-1] == None:
                read_source = core.testing.test_filename_[-1]
                if core.main.read_path_[-1]:
                    read_source = core.main.read_path_[-1] + '/' + core.testing.test_filename_[-1]
                if exists(read_source):
                    core.testing.test_f_[-1] = open(read_source, 'r')
                else:
                    core.testing.testMessage("File '{0}' does not exist; stopping test.".format(read_source), True)
                    core.testing.testStop(True)
            if core.testing.test_f_[-1] != None:
                line = re.sub('\n', '', line)
                test_line = core.testing.test_f_[-1].readline()
                if test_line != '':
                    test_line = re.sub('\n', '', test_line)
                    if line == test_line:
                        core.testing.testMessage('Passed: {0}'.format(line))
                        core.testing.test_pass_[-1] += 1
                    else:
                        core.testing.testMessage("Expected: '{0}'".format(test_line), True)
                        core.testing.testMessage("Received: '{0}'".format(line), True)
                        core.testing.test_fail_[-1] += 1
                else:
                    core.testing.testMessage('Unexpected EOF reached; stopping test.', True)
                    core.testing.testStop(True)
        except:
            core.testing.testMessage('Unexpected error: {0}'.format(line), True)
            traceback.print_exc()
    if not core.testing.testing_[-1]:
        print(line, file=stdio)

################################################################################
# process comments and gotos
################################################################################

def skipLine(line):
    if core.main.comment_mode_[-1] == -1: core.main.comment_mode_[-1] = 0
    if re.search('^\s*\/\*', line): core.main.comment_mode_[-1] = 1
    if re.search('\*\/\s*$', line): core.main.comment_mode_[-1] = -1
    if core.main.comment_mode_[-1] != 0: return True
    if re.search('^\s*\#', line): return True
    if re.search('^\s*\/\/', line): return True
    if re.search('^[\s-]*$', line): return True
    m = re.search('^\s*(\S*)\:\s*$', line)
    if m:
        if m.group(1) == core.main.goto_[-1]:
            core.main.goto_[-1] = None
        return True
    if core.main.goto_[-1]: return True
    return False

################################################################################
# process help files
################################################################################

def showHelp(topic, stop_running = False):
    helpfile = None
    if not topic:
        topic = 'usage'
    try:
        dir_path = dirname(realpath(__file__))
        help_path = dir_path + '/help/' + re.sub(' ', '-', topic).lower()
        if exists(help_path + '/_main.txt'):
            help_path += '/_main'
        helpfile = open(help_path + '.txt')
        for line in helpfile:
            print(textwrap.fill(line, core.main.terminal_width_))
    except FileNotFoundError:
        errorMessage(f"No help file for '{topic}' could be found.", True)
    finally:
        if helpfile:
            helpfile.close()
    if stop_running:
        core.main.running_[-1] = False
        popEnv()

################################################################################
# maintain an environment stack to facilitate nested file reads
################################################################################

def pushEnv():
    pushLists([
        core.main.running_,
        core.main.comment_mode_,
        core.main.infomsg_,
        core.main.output_,
        core.main.goto_,
        core.main.read_path_,
        core.main.elements_,
        core.main.formats_,
        core.main.headers_,
        core.main.justify_,
        core.main.padding_,
        core.main.width_,
        core.main.map_,
        core.main.timer_,
        core.main.timer_label_,
        core.main.timer_ts_
    ])
    pushLists([
        core.testing.testing_,
        core.testing.test_filename_,
        core.testing.test_f_,
        core.testing.test_pause_,
        core.testing.test_verbose_,
        core.testing.test_pass_,
        core.testing.test_fail_
    ])
    pushLists(bridge.plugin.getEnv())

def popEnv():
    popLists([
        core.main.running_,
        core.main.comment_mode_,
        core.main.infomsg_,
        core.main.output_,
        core.main.goto_,
        core.main.read_path_,
        core.main.elements_,
        core.main.formats_,
        core.main.headers_,
        core.main.justify_,
        core.main.padding_,
        core.main.width_,
        core.main.map_
    ])
    popLists([
        core.testing.testing_,
        core.testing.test_filename_,
        core.testing.test_f_,
        core.testing.test_pause_,
        core.testing.test_verbose_,
        core.testing.test_pass_,
        core.testing.test_fail_
    ])
    popLists(bridge.plugin.getEnv())

def pushLists(lists):
    if lists != None:
        for list in lists:
            if list != None:
                list.append(list[-1])

def popLists(lists):
    if lists != None:
        for list in lists:
            if list != None and len(list) > 1:
                if not core.main.read_inline_:
                    list.pop()
                else:
                    copy = list[-1]
                    list.pop()
                    list[-1] = copy

################################################################################
# messaging
################################################################################

def infoMessage(message):
    if core.main.infomsg_[-1] and core.main.output_[-1]: printLine('<i> ' + message)

def errorMessage(message, trace = False):
    printLine(core.ANSI.FG_RED + '<E> ' + message + core.ANSI.FG_DEFAULT, sys.stderr)
    if trace and core.cli.verbose_verbose_:
        traceback.print_exc()

################################################################################
# must be at the end of this code
################################################################################

parser = Parser()
