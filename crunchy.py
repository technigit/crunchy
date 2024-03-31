#!/usr/bin/env python3

'''
 * Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
'''

import fileinput, re, shutil, sys, textwrap, traceback
from os.path import dirname, exists, realpath

# class methods to set text colors
class ANSI():
    def set_display_attribute(code): return "\33[{attr}m".format(attr = code)
    FG_DEFAULT = set_display_attribute(0)
    FG_RED = set_display_attribute(31)
    FG_YELLOW = set_display_attribute(33)
    FG_GREEN = set_display_attribute(32)

####################
# global variables
####################

version_ = 'v0.0.11'

# &read recursion depth limit
max_read_depth_ = 5

# word wrap for help files
terminal_width_ = shutil.get_terminal_size().columns

# interactive mode affects UX for error handling
interactive_ = False

# show the header when needed
header_mode_ = False

# command-line options
ignore_stop_ = False
ignore_stop_reset_ = False
skip_testing_ = False
test_force_quiet_ = False
test_force_verbose_ = False

# these global variables can be reset
def initGlobals():
    global running_, comment_mode_, infomsg_, output_, goto_, read_path_
    global testing_, test_filename_, test_f_, test_pause_, test_verbose_, test_pass_, test_fail_
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_, catvalues_
    global elements_, headers_, justify_, width_, map_

    running_ = [True]
    comment_mode_ = [0]
    infomsg_ = [True]
    output_ = [True]
    goto_ = [None]
    read_path_ = [None]

    testing_ = [False]
    test_filename_ = [None]
    test_f_ = [None]
    test_pause_ = [False]
    test_verbose_ = [False]
    test_pass_ = [0]
    test_fail_ = [0]

    fulbal_ = [0.0]
    clrbal_ = [0.0]
    catfield_ = [None]
    clrfield_ = [None]
    incfield_ = [None]
    decfield_ = [None]
    catvalues_ = {}

    elements_ = None
    headers_ = [None]
    justify_ = [None]
    width_ = [None]
    map_ = [None]

####################
# functions
####################

def show_info(should_show = False):
    global interactive_
    if should_show or (len(sys.argv) == 1 and sys.stdin.isatty()):
        interactive_ = True
        printLine("""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
""" + version_ + """

To get help, enter &help
To exit interactive mode, use Ctrl-D
""")

################################################################################

def skipLine(line):
    global comment_mode_, goto_
    if comment_mode_[-1] == -1: comment_mode_[-1] = 0
    if re.search('^\s*\/\*', line): comment_mode_[-1] = 1
    if re.search('\*\/\s*$', line): comment_mode_[-1] = -1
    if comment_mode_[-1] != 0: return True
    if re.search('^\s*\#', line): return True
    if re.search('^\s*\/\/', line): return True
    if re.search('^[\s-]*$', line): return True
    m = re.search('^\s*(\S*)\:\s*$', line)
    if m:
        if m.group(1) == goto_[-1]:
            goto_[-1] = None
        return True
    if goto_[-1]: return True
    return False

####################

def makeHeaders():
    global elements_, width_, justify_
    width_[-1] = [None] * len(elements_)
    justify_[-1] = [None] * len(elements_)
    for i, element in enumerate(elements_):
        element = element.strip()
        m = re.search('^.*\D(\d*)$', element)
        if m:
            width_[-1][i] = int(m.group(1))
            element = re.search('^(.*\D)\d*$', element).group(1)
            justify_[-1][i] = '>'
            if re.search('\<$', element):
                justify_[-1][i] = '<'
            if re.search('\|$', element):
                justify_[-1][i] = '|'
            elements_[i] = re.sub('[\<\|\>]$', '', element)
        else:
            return None
    return elements_

####################

def getElements(line):
    delim = '~'
    line = re.sub('^\s*', '', line)
    line = re.sub('\s\s(\s*)', delim, line)
    elements_ = line.split(delim)
    for i, element in enumerate(elements_):
        if element == '-':
            elements_[i] = ' '
    return elements_

################################################################################

def ljustify(str, width):
    return str.ljust(width)[:width]

####################

def cjustify(str, width):
    return str.center(width)[:width]

####################

def rjustify(str, width):
    return str.rjust(width)[:width]

####################

def currency(num):
    return '${:,.2f}'.format(num)

################################################################################

def infoMessage(message):
    if infomsg_[-1] and output_[-1]: printLine('<i> ' + message)

####################

def errorMessage(message):
    printLine(ANSI.FG_RED + '<E> ' + message + ANSI.FG_DEFAULT, sys.stderr)

################################################################################

def testMessage(message, verbose = False):
    global test_verbose_
    if test_verbose_[-1] or verbose: print(ANSI.FG_YELLOW + '<T> ' + message + ANSI.FG_DEFAULT)

####################

def testStop(verbose = False):
    global testing_, test_filename_, test_f_, test_pause_, test_pass_, test_fail_
    testing_[-1] = False
    test_pause_[-1] = False
    if test_f_[-1] != None:
        eof_test = test_f_[-1].readline()
        if eof_test != '':
            testMessage('The test was unexpectedly interrupted.', True)
            while eof_test != '':
                test_fail_[-1] += 1
                eof_test = test_f_[-1].readline()
        test_f_[-1].close()
    test_f_[-1] = None
    testMessage('Test stopped.', verbose)
    total = test_pass_[-1] + test_fail_[-1]
    s = 's' if total != 1 else ''
    tested = str(total) + ' line' + s + ' tested: '
    if test_pass_[-1] > 0:
        passed = ANSI.FG_GREEN + str(test_pass_[-1]) + ' passed' + ANSI.FG_YELLOW + ' :: '
    else:
        passed = str(test_pass_[-1]) + ' passed :: '
    if test_fail_[-1] > 0:
        failed = ANSI.FG_RED + str(test_fail_[-1]) + ' failed' + ANSI.FG_YELLOW + ' :: '
    else:
        failed = str(test_fail_[-1]) + ' failed :: '
    testfile = test_filename_[-1]
    text_offset = 0 if total < 1000 else 2 # make room for big numbers
    testMessage(rjustify(tested, 18 + text_offset) + rjustify(passed, 24 + text_offset) + failed + testfile, True)
    test_filename_[-1] = ''

################################################################################

def printLine(line = '', stdio=sys.stdout):
    global testing_, test_filename_, test_f_, test_pass_, test_fail_
    if testing_[-1]:
        try:
            if test_f_[-1] == None:
                read_source = test_filename_[-1]
                if read_path_[-1]:
                    read_source = read_path_[-1] + '/' + test_filename_[-1]
                if exists(read_source):
                    test_f_[-1] = open(read_source, 'r')
                else:
                    testMessage('File \'' + read_source + '\' does not exist; stopping test.', True)
                    testStop(True)
            if test_f_[-1] != None:
                line = re.sub('\n', '', line)
                test_line = test_f_[-1].readline()
                if test_line != '':
                    test_line = re.sub('\n', '', test_line)
                    if line == test_line:
                        testMessage('Passed: ' + line)
                        test_pass_[-1] += 1
                    else:
                        testMessage("Expected: '{0}'".format(test_line), True)
                        testMessage("Received: '{0}'".format(line), True)
                        test_fail_[-1] += 1
                else:
                    testMessage('Unexpected EOF reached; stopping test.', True)
                    testStop(True)
        except:
            testMessage('Unexpected error: ' + line, True)
            traceback.print_exc()
    if not testing_[-1]:
        print(line, file=stdio)

################################################################################

def pushGlobals(listnames):
    for listname in listnames:
        if listname in globals():
            list = globals()[listname]
            list.append(list[-1])
        else:
            errorMessage('pushGlobals: ' + listname + ' not found in globals.')

################################################################################

def popGlobals(listnames):
    for listname in listnames:
        if listname in globals():
            list = globals()[listname]
            if len(list) > 1:
                list.pop()
        else:
            errorMessage('popGlobals: ' + listname + ' not found in globals.')

################################################################################

def pushEnv():
    pushGlobals(['running_', 'comment_mode_', 'infomsg_', 'output_', 'goto_', 'read_path_'])
    pushGlobals(['testing_', 'test_filename_', 'test_f_', 'test_pause_', 'test_verbose_', 'test_pass_', 'test_fail_'])
    pushGlobals(['headers_', 'justify_', 'width_', 'map_'])

################################################################################

def popEnv():
    popGlobals(['running_', 'comment_mode_', 'infomsg_', 'output_', 'goto_', 'read_path_'])
    popGlobals(['testing_', 'test_filename_', 'test_f_', 'test_pause_', 'test_verbose_', 'test_pass_', 'test_fail_'])
    popGlobals(['headers_', 'justify_', 'width_', 'map_'])

################################################################################

def debugList(listname, list = []):
    if listname in globals():
        list = globals()[listname]
    print(listname + ':  ', end='')
    for i in list:
        print('`' + str(i), end='')
    print('')

################################################################################

def parseDirective(line):
    global running_, infomsg_, output_, goto_, max_read_depth_, read_path_
    global testing_, test_filename_, test_pause, test_verbose_, test_pass_, test_fail_
    global ignore_stop_, ignore_stop_reset_, skip_testing_, test_force_quiet_, test_force_verbose_
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_, map_
    global headers_, header_mode_
    argtrim = ''
    arg = None
    m = re.search('^\s*\S(\S*)\s(.*)$', line)
    if m:
        arg = m.group(2)
        argtrim = arg.strip()
    else:
        m = re.search('^\s*\S(\S*)$', line)
        arg = None
        argtrim = None
    cmd = m.group(1)

    ####################

    if cmd == 'cat':
        if not argtrim:
            prettyCat('All')
        elif not ' ' in argtrim:
            prettyCat(argtrim)
        else:
            prettyCatHeader()
            for category in argtrim.split():
                prettyCat(category, True)

    ####################

    elif cmd == 'cd':
        read_path_[-1] = argtrim
        if read_path_[-1]:
            infoMessage('Setting current working directory to \'' + read_path_[-1] + '\'.')
        else:
            infoMessage('Resetting current working directory.')

    ####################

    elif cmd == 'goto':
        goto_[-1] = argtrim
        if argtrim:
            infoMessage('Skipping to \'' + goto_[-1] + '\'.')
        else:
            infoMessage('Usage: &goto <label>')

    ####################

    elif cmd == 'header':
        if headers_[-1]:
            header_mode_ = True
            parseLine('  '.join(headers_[-1]))
        else:
            errorMessage('No header information found.')

    ####################

    elif cmd == 'help':
        showHelp(argtrim)

    ####################

    elif cmd == 'init':
        if argtrim:
            fulbal_[-1] = float(argtrim)
            clrbal_[-1] = fulbal_[-1]
            infoMessage('Initializing balance to {0}.'.format(currency(fulbal_[-1])))
        else:
            infoMessage('Usage: &init <float>')

    ####################

    elif cmd == 'map':
        show_usage = False
        if argtrim:
            premap = getElements(argtrim)
            map_[-1] = [None] * len(premap)
            try:
                for m, element in enumerate(premap):
                    map_[-1][int(premap[m]) - 1] = m + 1
                infoMessage('Fields were remapped.')
            except ValueError:
                show_usage = True
        else:
            show_usage = True
        if show_usage:
            infoMessage('Usage: &map <int><space><space><int>...')

    ####################

    elif cmd == 'output' and arg == 'on':
        output_[-1] = True
        infoMessage('Output mode is on.')
    elif cmd == 'output' and arg == 'off':
        infoMessage('Output mode is off.')
        output_[-1] = False
    elif cmd =='output':
        infoMessage('Usage: &output on|off')

    ####################

    elif cmd == 'print' and output_[-1]:
        printLine(arg) if arg is not None else printLine()
    elif cmd == 'print' and not output_[-1]:
        pass

    ####################

    elif cmd == 'read':
        if argtrim:
            read_source = argtrim
            if read_path_[-1]:
                read_source = read_path_[-1] + '/' + argtrim
            if max_read_depth_ > 0:
                max_read_depth_ = max_read_depth_ - 1
                infoMessage('Reading file ' + read_source + '.')
                if exists(read_source):
                    f = open(read_source, 'r')
                    pushEnv()
                    try:
                        for read_line in f:
                            read_line = re.sub('\n', '', read_line)
                            if not skipLine(read_line): parseLine(read_line)
                            if not running_[-1]: break
                    except IndexError:
                        errorMessage('Badly formed data: ' + read_line)
                    except ValueError:
                        errorMessage('Invalid input: ' + read_line)
                    except:
                        errorMessage('Unexpected error.')
                        traceback.print_exc()
                    finally:
                        f.close()
                        if testing_[-1]:
                            testStop()
                        popEnv()
                        infoMessage('Finished reading file ' + read_source + '.')
                else:
                    errorMessage(cmd + ': File \'' + read_source + '\' does not exist.')
                max_read_depth_ = max_read_depth_ + 1
            else:
                errorMessage(cmd + ': Nested level too deep; will not read ' + read_source + '.')
        else:
            infoMessage('Usage: &read <filename>')

    ####################

    elif cmd == 'set':
        show_usage = False
        if argtrim:
            parts = argtrim.split()
            if len(parts) > 1:
                if (parts[0] == 'catfield'):
                    catfield_[-1] = int(parts[1])
                    infoMessage('Setting category field to ' + str(catfield_[-1]) + '.')
                elif (parts[0] == 'clrfield'):
                    clrfield_[-1] = int(parts[1])
                    infoMessage('Setting clear field to ' + str(clrfield_[-1]) + '.')
                elif (parts[0] == 'decfield'):
                    decfield_[-1] = int(parts[1])
                    infoMessage('Setting decrement field to ' + str(decfield_[-1]) + '.')
                elif (parts[0] == 'incfield'):
                    incfield_[-1] = int(parts[1])
                    infoMessage('Setting increment field to ' + str(incfield_[-1]) + '.')
                else:
                    show_usage = True
            else:
                show_usage = True
        else:
            show_usage = True
        if show_usage:
            infoMessage('Usage: &set catfield <int> | clrfield <int> | decfield <int> | incfield <int>')

    ####################

    elif cmd == 'stop':
        if not ignore_stop_:
            if testing_[-1]:
                testStop()
            running_[-1] = False
        if ignore_stop_reset_:
            if testing_[-1]:
                testStop()
            initGlobals()

    ####################

    elif cmd == 'test' and skip_testing_:
        pass
    elif cmd == 'test':
        if argtrim == None:
            testMessage(cmd + ': parameters required.')
        elif argtrim.startswith('start'):
            if not testing_[-1]:
                m = re.search('^start\s+(\S*)$', argtrim)
                if m:
                    test_filename_[-1] = m.group(1)
                    testing_[-1] = True
                    test_pause_[-1] = False
                    test_pass_[-1] = 0
                    test_fail_[-1] = 0
                    testMessage('Test started with \'' + test_filename_[-1] + '\'')
                else:
                    testMessage('Test filename not specified.')
            else:
                testMessage('Test is already running (' + test_filename_[-1] + ').')
        elif argtrim == 'pause':
            if testing_[-1]:
                test_pause_[-1] = True
                testMessage('Test paused.')
            else:
                testMessage('No test is currently running.')
        elif argtrim == 'resume':
            if testing_[-1]:
                test_pause_[-1] = False
                testMessage('Test resumed.')
            else:
                testMessage('No test is currently running.')
        elif argtrim == 'verbose':
            if not test_force_quiet_:
                test_verbose_[-1] = True
                testMessage('Test mode set to verbose.')
        elif argtrim == 'quiet':
            if not test_force_verbose_:
                test_verbose_[-1] = False
                testMessage('Test mode set to quiet.')
        elif argtrim == 'stop':
            testStop()
        else:
            testMessage(cmd + ': invalid parameter.')

    ####################

    elif cmd == 'infomsg' and arg == 'on':
        infomsg_[-1] = True
        infoMessage('Infomsg mode is on.')
    elif cmd == 'infomsg' and arg == 'off':
        infomsg_[-1] = False

    ####################

    else:
        errorMessage('Invalid directive: ' + line)

####################

def prettyCatHeader():
    cat_header_width = width_[-1][catfield_[-1]]
    dec_header = headers_[-1][decfield_[-1]]
    dec_header_width = width_[-1][decfield_[-1]]
    inc_header = headers_[-1][incfield_[-1]]
    inc_header_width = width_[-1][incfield_[-1]]
    printLine('{0} {1}  {2}'.format(
        rjustify('', cat_header_width + 2),
        rjustify(dec_header, dec_header_width + 3),
        rjustify(inc_header, inc_header_width + 3))
    )

####################

def prettyCat(category, use_header = False):
    global incfield_, decfield_
    catpay_key = category + 'payamt'
    catdep_key = category + 'depamt'
    if not catpay_key in catvalues_ or not catdep_key in catvalues_:
        catpay_key = 'payamt'
        catdep_key = 'depamt'
    cat_header_width = width_[-1][catfield_[-1]]
    dec_header = headers_[-1][decfield_[-1]]
    dec_header_width = width_[-1][decfield_[-1]]
    catpay_currency = currency(catvalues_[catpay_key])
    inc_header = headers_[-1][incfield_[-1]]
    inc_header_width = width_[-1][incfield_[-1]]
    catdep_currency = currency(catvalues_[catdep_key])
    if not use_header:
        printLine('{0} :: {1}: {2}  {3}: {4}'.format(
            rjustify(category, cat_header_width),
            rjustify(dec_header, dec_header_width),
            rjustify(catpay_currency, dec_header_width + 3),
            rjustify(inc_header, inc_header_width),
            rjustify(catdep_currency, inc_header_width + 3))
        )
    else:
        printLine('{0} | {1}  {2}'.format(
            rjustify(category, cat_header_width),
            rjustify(catpay_currency, dec_header_width + 3),
            rjustify(catdep_currency, inc_header_width + 3))
        )

################################################################################

def parseOptions():
    global ignore_stop_, ignore_stop_reset_, skip_testing_, test_force_quiet_, test_force_verbose_
    if len(sys.argv) == 1:
        return
    input_files = []
    skip = False
    for i, option in enumerate(sys.argv):
        if skip:
            skip = False
            continue
        if option.startswith('-'):
            if option in ['-is', '--ignore-stop']:
                ignore_stop_ = True
            elif option in ['-isr', '--ignore-stop-reset']:
                ignore_stop_ = True
                ignore_stop_reset_ = True
            elif option in ['-h', '---help']:
                topic = None
                if i < len(sys.argv) - 1:
                    topic = sys.argv[i+1]
                    skip = True
                showHelp(topic, True)
            elif option in ['-st', '--skip-testing']:
                skip_testing_ = True
            elif option in ['-tv', '--test-verbose']:
                parseDirective('&test verbose')
            elif option in ['-tfv', '--test-force-verbose']:
                test_force_verbose_ = True
                parseDirective('&test verbose')
            elif option in ['-tfq', '--test-force-quiet']:
                test_force_quiet_ = True
                parseDirective('&test quiet')
            else:
                errorMessage('Unknown option: ' + option)
                printLine()
                showHelp('usage', True)
        elif i > 0:
            input_files.append(option)
    return input_files

################################################################################

def parseLine(line):
    global running_
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_, catvalues_
    global elements_, headers_, header_mode_
    if re.search('^\s*&', line):
        parseDirective(line)
    else:
        elements_ = getElements(line)
        if headers_[-1] == None:
            headers_[-1] = makeHeaders()
            header_mode_ = True
        if headers_[-1] == None:
            errorMessage('Invalid header configuration: ' + line)
            running_[-1] = False
            popEnv()
            return
        out = ''
        for i, element in enumerate(elements_):
            m = i
            if map_[-1] != None:
                m = map_[-1][i] - 1
            if not headers_[-1][m].startswith('#'):
                align = justify_[-1][m]
                if align == '<':
                    out += ljustify(elements_[m], width_[-1][m]) + ' '
                if align == '|':
                    out += cjustify(elements_[m], width_[-1][m]) + ' '
                if align == '>':
                    out += rjustify(elements_[m], width_[-1][m]) + ' '
        payamt = 0.0
        depamt = 0.0
        if decfield_[-1] != None:
            payamt = elements_[decfield_[-1]]
            payamt = re.sub('^\d\.-', '', payamt)
            if payamt.strip() == '':
                payamt = 0.0
        else:
            errorMessage('Decrement field is not set.')
        if incfield_[-1] != None:
            depamt = elements_[incfield_[-1]]
            depamt = re.sub('^\d\.-', '', depamt)
            if depamt.strip() == '':
                depamt = 0.0
        else:
            errorMessage('Increment field is not set.')
        try:
            if not 'payamt' in catvalues_: catvalues_['payamt'] = 0.0
            catvalues_['payamt'] += float(payamt)
            if not 'depamt' in catvalues_: catvalues_['depamt'] = 0.0
            catvalues_['depamt'] += float(depamt)
            fulbal_[-1] -= float(payamt)
            fulbal_[-1] += float(depamt)
            if elements_[clrfield_[-1]] != ' ':
                clrbal_[-1] -= float(payamt)
                clrbal_[-1] += float(depamt)
            if catfield_[-1] != None and elements_[catfield_[-1]] != ' ':
                catpay_key = elements_[catfield_[-1]] + 'payamt'
                catdep_key = elements_[catfield_[-1]] + 'depamt'
                if not catpay_key in catvalues_: catvalues_[catpay_key] = 0.0
                catvalues_[catpay_key] += float(payamt)
                if not catdep_key in catvalues_: catvalues_[catdep_key] = 0.0
                catvalues_[catdep_key] += float(depamt)
        except ValueError:
            pass
        if output_[-1]:
            if header_mode_:
                printLine('{0}'.format(out))
            else:
                printLine('{0}{1:8.2f} {2:8.2f}'.format(out, fulbal_[-1], clrbal_[-1]))
        header_mode_ = False

################################################################################

def processData():
    global running_, testing_
    should_stop = True
    try:
        with fileinput.FileInput(files=(filenames), mode='r') as input:
            for line in input:
                line = re.sub('\n', '', line)
                if not skipLine(line): parseLine(line)
                if not running_[-1]: break
    except FileNotFoundError as e:
        errorMessage('Input file not found: ' + e.filename)
    except IndexError:
        errorMessage('Badly formed data: ' + line)
        should_stop = False
    except ValueError:
        errorMessage('Invalid input: ' + line)
        should_stop = False
    except KeyboardInterrupt:
        errorMessage('Interrupted.')
    except:
        errorMessage('Unexpected error.')
        traceback.print_exc()
    finally:
        fileinput.close()
        if testing_[-1]:
            testStop()
    if should_stop:
        running_[-1] = False

################################################################################

def showHelp(topic, stop_running = False):
    global running_
    helpfile = None
    if not topic:
        topic = 'usage'
    try:
        dir_path = dirname(realpath(__file__))
        helpfile = open(dir_path + '/help/' + re.sub(' ', '-', topic).lower() + '.txt')
        for line in helpfile:
            print(textwrap.fill(line, terminal_width_))
    except FileNotFoundError:
        errorMessage('No help file for \'' + topic + '\' could be found.')
    finally:
        if helpfile:
            helpfile.close()
    if stop_running:
        running_[-1] = False
        popEnv()

####################
# start here
####################

initGlobals()

# show information when starting in interactive mode
show_info()

# process command-line options
filenames = parseOptions()

# main parsing loop
while running_[-1]:
    processData()
    if not interactive_:
        break

# gracefully handle uncompleted goto directives
if goto_[-1]:
    errorMessage('EOF reached before tag \'' + goto_[-1] + '\'.')
