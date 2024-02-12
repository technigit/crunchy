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
        print("""
Crunchy Report Generator aka Crunch Really Useful Numbers Coded Hackishly
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

def getElements(line):
    delim = '~'
    line = re.sub('^\s*', '', line)
    line = re.sub('\s\s(\s*)', delim, line)
    elements_ = line.split(delim)
    for i, element in enumerate(elements_):
        if element == '-':
            elements_[i] = ' '
    return elements_

def ljustify(str, width):
    return str.ljust(width)[:width]

def cjustify(str, width):
    return str.center(width)[:width]

def rjustify(str, width):
    return str.rjust(width)[:width]

def infoMessage(message):
    if infomsg_ and output_: print('<i> ' + message)

def errorMessage(message):
    print('<E> ' + message, file=sys.stderr)

def debugList(listname, list = []):
    if listname in globals():
        list = globals()[listname]
    print(listname + ':  ', end='')
    for i in list:
        print('`' + str(i), end='')
    print('')

def parseDirective(line):
    global running_, infomsg_, output_, goto_, max_read_depth_, read_path_
    global fulbal_, clrbal_, catfield_, clrfield_, incfield_, decfield_, map_
    argtrim = ''
    arg = None
    m = re.search('^\s*\S(\S*)\s(\s*)(\S.*\S)(\s*)$', line)
    if m:
        cmd = m.group(1)
        arg = m.group(2) + m.group(3) + m.group(4)
        argtrim = m.group(3)
    else:
        m = re.search('^\s*\S(\S*)$', line)
        if m:
            cmd = m.group(1)
        else:
            m = re.search('^\s*\S(\S*)\s(\S*)\s(\S*)\s*$', line)
            if m:
                cmd = m.group(1)
                arg1 = m.group(2)
                arg2 = m.group(3)
    if cmd == 'cd':
        read_path_ = argtrim
        if read_path_:
            infoMessage('Setting current working directory to \'' + read_path_ + '\'.')
        else:
            infoMessage('Resetting current working directory.')
    elif cmd == 'goto':
        goto_ = argtrim
        infoMessage('Skipping to \'' + goto_ + '\'.')
    elif cmd == 'header': pass
    elif cmd == 'init':
        fulbal_ = float(argtrim)
        clrbal_ = fulbal_
        infoMessage('Initializing balance to {:.2f}'.format(fulbal_) + '.')
    elif cmd == 'map':
        premap = getElements(argtrim)
        map_ = [None] * len(premap)
        for m, element in enumerate(premap):
            map_[int(premap[m]) - 1] = m + 1
        infoMessage('Fields were remapped.')
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
            print('{0} {1:8.2f} ({2:8.2f})'.format(out, fulbal_, clrbal_))

####################
# start here
####################

# show information when starting in interactive mode
show_info()

# main parsing loop
try:
    for line in fileinput.input():
        if not running_: break
        if not skipLine(line): parseLine(re.sub('\n', '', line))
except FileNotFoundError:
    errorMessage('Input file not found.')
finally:
    fileinput.close()
if goto_:
    errorMessage('EOF reached before tag \'' + goto_ + '\'.')
