#!/usr/local/bin/python3

'''
 * Copyright (c) 2000, 2022, 2023 Andy Warmack
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 *
'''

import fileinput, re, sys
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

####################
# functions
####################

def show_info(should_show = False):
    if should_show or len(sys.argv) == 1:
        print("""
Crunch Really Useful Numbers Coded Hackishly
This is a test.
""")

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

def infoMessage(message):
    if infomsg_ and output_: print('<i> ' + message)

def errorMessage(message):
    print('<E> ' + message, file=sys.stderr)

def parseDirective(line):
    global running_, output_, infomsg_, goto_, max_read_depth_, read_path_
    argtrim = ''
    arg = None
    m = re.search('^\s*\S(\S*)\s(\s*)(\S.*\S)(\s*)\n$', line)
    if m:
        cmd = m.group(1)
        arg = m.group(2) + m.group(3) + m.group(4)
        argtrim = m.group(3)
    else:
        m = re.search('^\s*\S(\S*)$', line)
        cmd = m.group(1)
    if cmd == 'cd':
        read_path_ = argtrim
        if read_path_:
            infoMessage('Setting current working directory to \'' + read_path_ + '\'.')
        else:
            infoMessage('Resetting current working directory.')
    elif cmd == 'goto':
        goto_ = argtrim
        infoMessage('Skipping to \'' + goto_ + '\'')
    elif cmd == 'header': pass
    elif cmd == 'init': pass
    elif cmd == 'map': pass
    elif cmd == 'output' and arg == 'on':
        output_ = True
        infoMessage('Output mode is on.')
    elif cmd == 'output' and arg == 'off':
        infoMessage('Output mode is off.')
        output_ = False
    elif cmd == 'print' and output_:
        print(arg) if arg is not None else print()
    elif cmd == 'print' and not output_:
        pass
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
                errorMessage('&read: File \'' + read_source + '\' does not exist.')
            max_read_depth_ = max_read_depth_ + 1
        else:
            errorMessage('&read: Nested level too deep; will not read ' + read_source + '.')
    elif cmd == 'set': pass
    elif cmd == 'stop':
        running_ = False
    elif cmd == 'infomsg' and arg == 'on':
        infomsg_ = True
        infoMessage('Infomsg mode is on.')
    elif cmd == 'infomsg' and arg == 'off':
        infomsg_ = False
    else:
        m = re.search('^(.*)\n$', line)
        errorMessage('Invalid directive: ' + m.group(1))

def parseLine(line):
    if re.search('^\s*&', line): parseDirective(line)

####################
# start here
####################

# show information when starting in interactive mode
show_info()

# main parsing loop
try:
    for line in fileinput.input():
        if not running_: break
        if not skipLine(line): parseLine(line)
except FileNotFoundError:
    errorMessage('Input file not found.')
finally:
    fileinput.close()
if goto_:
    errorMessage('EOF reached before tag \'' + goto_ + '\'.')
