#!/usr/local/bin/python3

'''
 * Copyright (c) 2000, 2022, 2023 Andy Warmack
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
'''

import fileinput, re, sys, traceback
from os.path import exists

####################
# global variables
####################

running_ = True
comment_mode_ = 0
infomsg_ = True
output_ = True
goto_ = ''
max_read_depth_ = 5
read_path_ = ''

testing_ = False
test_filename_ = None
test_f_ = None
test_pause_ = False
test_verbose_ = False
test_pass_ = 0
test_fail_ = 0

fulbal_ = 0.0
clrbal_ = 0.0
catfield_ = None
clrfield_ = None
incfield_ = None
decfield_ = None

elements_ = None
headers_ = None
justify_ = None
width_ = None
map_ = None

####################
# functions
####################

def show_info(should_show = False):
    if should_show or len(sys.argv) == 1:
        printLine("""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
""")

################################################################################

def skipLine(line):
    global comment_mode_, goto_
    if comment_mode_ == -1: comment_mode_ = 0
    if re.search('^\s*\/\*', line): comment_mode_ = 1
    if re.search('\*\/\s*$', line): comment_mode_ = -1
    if comment_mode_ != 0: return True
    if re.search('^\s*\#', line): return True
    if re.search('^\s*\/\/', line): return True
    if re.search('^[\s-]*$', line): return True
    m = re.search('^\s*(\S*)\:\s*$', line)
    if m:
        if m.group(1) == goto_:
            goto_ = ''
        return True
    if goto_: return True
    return False

####################

def makeHeaders():
    global elements_, width_, justify_
    width_ = [None] * len(elements_)
    justify_ = [None] * len(elements_)
    for i, element in enumerate(elements_):
        element = element.strip()
        width_[i] = int(re.search('^.*\D(\d*)$', element).group(1))
        element = re.search('^(.*\D)\d*$', element).group(1)
        justify_[i] = '>'
        if re.search('\<$', element):
            justify_[i] = '<'
        if re.search('\|$', element):
            justify_[i] = '|'
        elements_[i] = re.sub('[\<\|\>]$', '', element)
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

################################################################################

def infoMessage(message):
    if infomsg_ and output_: printLine('<i> ' + message)

####################

def errorMessage(message):
    printLine('<E> ' + message, sys.stderr)

################################################################################

def testMessage(message, verbose = False):
    global test_verbose_
    if test_verbose_ or verbose: print('<T> ' + message)

####################

def testStop(verbose = False):
    global testing_, test_filename_, test_f_, test_pause_, test_pass_, test_fail_
    test_filename_ = ''
    testing_ = False
    test_pause_ = False
    if test_f_ != None: test_f_.close()
    testMessage('Test stopped.', verbose)
    total = test_pass_ + test_fail_
    s = 's' if total != 1 else ''
    testMessage(str(test_pass_ + test_fail_) + ' line' + s + ' tested: ' + str(test_pass_) + ' passed, ' + str(test_fail_) + ' failed', True)

################################################################################

def printLine(line = '', stdio=sys.stdout):
    global testing_, test_filename_, test_f_, test_pass_, test_fail_
    if testing_:
        try:
            if test_f_ == None:
                if exists(test_filename_):
                    test_f_ = open(test_filename_, 'r')
                else:
                    testMessage('File \'' + test_filename_ + '\' does not exist; stopping test.', True)
                    testStop(True)
            if test_f_ != None:
                line = re.sub('\n', '', line)
                test_line = test_f_.readline()
                if test_line != '':
                    test_line = re.sub('\n', '', test_line)
                    if line == test_line:
                        testMessage('Passed: ' + line)
                        test_pass_ += 1
                    else:
                        testMessage('Expected: ' + test_line, True)
                        testMessage('Received: ' + line, True)
                        test_fail_ += 1
                else:
                    testMessage('Unexpected EOF reached; stopping test.', True)
                    testStop(True)
        except:
            testMessage('Unexpected error: ' + line, True)
            traceback.print_exc()
    if not testing_:
        print(line, file=stdio)

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
    global testing_, test_filename_, test_pause, test_verbose_
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_, map_
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

    if cmd == 'cd':
        read_path_ = argtrim
        if read_path_:
            infoMessage('Setting current working directory to \'' + read_path_ + '\'.')
        else:
            infoMessage('Resetting current working directory.')

    ####################

    elif cmd == 'goto':
        goto_ = argtrim
        infoMessage('Skipping to \'' + goto_ + '\'.')

    ####################

    elif cmd == 'header': pass

    ####################

    elif cmd == 'init':
        fulbal_ = float(argtrim)
        clrbal_ = fulbal_
        infoMessage('Initializing balance to {:.2f}'.format(fulbal_) + '.')

    ####################

    elif cmd == 'map':
        premap = getElements(argtrim)
        map_ = [None] * len(premap)
        for m, element in enumerate(premap):
            map_[int(premap[m]) - 1] = m + 1
        infoMessage('Fields were remapped.')

    ####################

    elif cmd == 'output' and arg == 'on':
        output_ = True
        infoMessage('Output mode is on.')
    elif cmd == 'output' and arg == 'off':
        infoMessage('Output mode is off.')
        output_ = False

    ####################

    elif cmd == 'print' and output_:
        printLine(arg) if arg is not None else printLine()
    elif cmd == 'print' and not output_:
        pass

    ####################

    elif cmd == 'read':
        read_source = argtrim
        if read_path_:
            read_source = read_path_ + '/' + argtrim
        if max_read_depth_ > 0:
            max_read_depth_ = max_read_depth_ - 1
            infoMessage('Reading file ' + read_source + '.')
            if exists(read_source):
                f = open(read_source, 'r')
                for read_line in f:
                    if not skipLine(read_line): parseLine(read_line)
                f.close()
                infoMessage('Finished reading file ' + read_source + '.')
            else:
                errorMessage(cmd + ': File \'' + read_source + '\' does not exist.')
            max_read_depth_ = max_read_depth_ + 1
        else:
            errorMessage(cmd + ': Nested level too deep; will not read ' + read_source + '.')

    ####################

    elif cmd == 'set':
        parts = argtrim.split(' ')
        if (parts[0] == 'catfield'):
            catfield_ = int(parts[1])
            infoMessage('Setting category field to ' + str(catfield_) + '.')
        elif (parts[0] == 'clrfield'):
            clrfield_ = int(parts[1])
            infoMessage('Setting clear field to ' + str(clrfield_) + '.')
        elif (parts[0] == 'decfield'):
            decfield_ = int(parts[1])
            infoMessage('Setting decrement field to ' + str(decfield_) + '.')
        elif (parts[0] == 'incfield'):
            incfield_ = int(parts[1])
            infoMessage('Setting increment field to ' + str(incfield_) + '.')

    ####################

    elif cmd == 'stop':
        running_ = False

    ####################

    elif cmd == 'test':
        if argtrim == None:
            test(cmd + ': parameters required.')
        elif argtrim.startswith('start'):
            if not testing_:
                m = re.search('^start\s+(\S*)$', argtrim)
                if m:
                    test_filename_ = m.group(1)
                    testing_ = True
                    test_pause_ = False
                    testMessage('Test started with \'' + test_filename_ + '\'')
                else:
                    testMessage('Test filename not specified.')
            else:
                testMessage('Test is already running (' + test_filename_ + ').')
        elif argtrim == 'pause':
            if testing_:
                test_pause_ = True
                testMessage('Test paused.')
            else:
                testMessage('No test is currently running.')
        elif argtrim == 'resume':
            if testing_:
                test_pause_ = False
                testMessage('Test resumed.')
            else:
                testMessage('No test is currently running.')
        elif argtrim == 'verbose':
            test_verbose_ = True
            testMessage('Test mode set to verbose.')
        elif argtrim == 'quiet':
            test_verbose_ = False
            testMessage('Test mode set to quiet.')
        elif argtrim == 'stop':
            testStop()
        else:
            test(cmd + ': invalid parameter.')

    ####################

    elif cmd == 'infomsg' and arg == 'on':
        infomsg_ = True
        infoMessage('Infomsg mode is on.')
    elif cmd == 'infomsg' and arg == 'off':
        infomsg_ = False

    ####################

    else:
        errorMessage('Invalid directive: ' + line)

################################################################################

def parseLine(line):
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_
    global elements_, headers_
    if re.search('^\s*&', line):
        parseDirective(line)
    else:
        elements_ = getElements(line)
        if headers_ == None:
            headers_ = makeHeaders()
        out = ''
        for i, element in enumerate(elements_):
            m = i
            if map_ != None:
                m = map_[i] - 1
            if not headers_[m].startswith('#'):
                align = justify_[m]
                if align == '<':
                    out = out + ljustify(elements_[m], width_[m]) + ' '
                if align == '|':
                    out = out + cjustify(elements_[m], width_[m]) + ' '
                if align == '>':
                    out = out + rjustify(elements_[m], width_[m]) + ' '
        payamt = 0.0
        depamt = 0.0
        if decfield_ != None:
            payamt = elements_[decfield_]
            payamt = re.sub('^\d\.-', '', payamt)
            if payamt.strip() == '':
                payamt = 0.0
        else:
            errorMessage('Decrement field is not set.')
        if incfield_ != None:
            depamt = elements_[incfield_]
            depamt = re.sub('^\d\.-', '', depamt)
            if depamt.strip() == '':
                depamt = 0.0
        else:
            errorMessage('Increment field is not set.')
        try:
            fulbal_ = fulbal_ - float(payamt)
            fulbal_ = fulbal_ + float(depamt)
        except ValueError:
            pass
        if output_:
            printLine('{0} {1:8.2f} ({2:8.2f})'.format(out, fulbal_, clrbal_))

####################
# start here
####################

# show information when starting in interactive mode
show_info()

try:

    # main parsing loop
    for line in fileinput.input():
        line = re.sub('\n', '', line)
        if not skipLine(line): parseLine(line)
        if not running_: break

except FileNotFoundError:
    errorMessage('Input file not found.')
except ValueError:
    errorMessage('Invalid input: ' + line)
except:
    errorMessage('Unexpected error: ' + line)
    traceback.print_exc()
finally:
    fileinput.close()
    if testing_:
        testStop()

if goto_:
    errorMessage('EOF reached before tag \'' + goto_ + '\'.')
