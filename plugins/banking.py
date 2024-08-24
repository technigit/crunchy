#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Banking plugin
#
################################################################################

import re

import core
from core_functions import ljustify, rjustify, currency
from core_functions import preParse
from core_functions import Parser, unrecognizedOption
from core_functions import formatElementByValue
from core_functions import isDirective
from core_functions import printLine
from core_functions import infoMessage, errorMessage

def identify(): return 'banking'

class my():
    fulbal_ = []
    clrbal_ = []
    catfield_ = []
    clrfield_ = []
    incfield_ = []
    decfield_ = []
    catvalues_ = []
    statvalues_ = []

def reset():
    my.fulbal_ = [0.0]
    my.clrbal_ = [0.0]
    my.catfield_ = [None]
    my.clrfield_ = [None]
    my.incfield_ = [None]
    my.decfield_ = [None]
    my.catvalues_ = [{}]
    my.statvalues_ = [{}]

class cli():
    override_init = False

reset()

def getEnv():
    return [
        my.fulbal_,
        my.clrbal_,
        my.catfield_,
        my.clrfield_,
        my.incfield_,
        my.decfield_,
        my.catvalues_,
        my.statvalues_
    ]

# min-max boundaries for stats
stats_min = 0.0
stats_max = 9999999.0

################################################################################
# parse plugin-specific directives, but pre-parse for core directives first
################################################################################

def parseMyDirective(line):
    p = Parser()
    p.preParseDirective(line)
    if p.done:
        return
    arg = p.arg
    argtrim = p.argtrim
    cmd = p.cmd
    options = p.options

    ####################

    if cmd == 'init':
        if argtrim:
            if not cli.override_init:
                my.fulbal_[-1] = float(argtrim)
                my.clrbal_[-1] = my.fulbal_[-1]
                my.statvalues_[-1]['init'] = my.fulbal_[-1]
                infoMessage('Initializing balance to {0}.'.format(currency(my.fulbal_[-1])))
            else:
                infoMessage('Overriding &init directive.')
        else:
            p.invalidUsage('&init <float>')

    ####################

    elif cmd == 'set':
        show_usage = False
        if argtrim:
            parts = argtrim.split()
            if len(parts) > 1:
                if (parts[0] == 'catfield'):
                    my.catfield_[-1] = int(parts[1])
                    infoMessage('Setting category field to {0}.'.format(str(my.catfield_[-1])))
                elif (parts[0] == 'clrfield'):
                    my.clrfield_[-1] = int(parts[1])
                    infoMessage('Setting clear field to {0}.'.format(str(my.clrfield_[-1])))
                elif (parts[0] == 'decfield'):
                    my.decfield_[-1] = int(parts[1])
                    infoMessage('Setting decrement field to {0}.'.format(str(my.decfield_[-1])))
                elif (parts[0] == 'incfield'):
                    my.incfield_[-1] = int(parts[1])
                    infoMessage('Setting increment field to {0}.'.format(str(my.incfield_[-1])))
                else:
                    show_usage = True
            else:
                show_usage = True
        else:
            show_usage = True
        if show_usage:
            p.invalidUsage('&set [ catfield <int> | clrfield <int> | decfield <int> | incfield <int> ]')

    ####################

    elif cmd == 'stats':
        init = False
        simple = True
        for option in options:
            if option in ['-f', '--full']:
                simple = False
            elif option in ['-i', '--init']:
                init = True
            else:
                unrecognizedOption(option)
        if init:
            my.catvalues_ = [{}]
            my.statvalues_ = [{}]
            infoMessage('Stats initialized.')
        elif simple:
            if not argtrim:
                simpleStats('All')
            elif not ' ' in argtrim:
                simpleStats(argtrim)
            else:
                simpleStatsHeader()
                for category in argtrim.split():
                    simpleStats(category, True)
                if core.main.output_[-1]:
                    printLine()
        else:
            if not argtrim:
                moreStats('All')
            elif not ' ' in argtrim:
                moreStats(argtrim)
            else:
                for category in argtrim.split():
                    moreStats(category)

    ####################

    else:
        p.invalidDirective()

################################################################################
# display banking stats in simple and complex formats
################################################################################

def simpleStatsHeader():
    cat_header_width = core.main.width_[-1][my.catfield_[-1]]
    dec_header = core.main.headers_[-1][my.decfield_[-1]]
    dec_header_width = core.main.width_[-1][my.decfield_[-1]]
    inc_header = core.main.headers_[-1][my.incfield_[-1]]
    inc_header_width = core.main.width_[-1][my.incfield_[-1]]
    if core.main.output_[-1]:
        printLine('{0} {1}  {2}'.format(
            rjustify('', cat_header_width + 2),
            rjustify(dec_header, dec_header_width + 3),
            rjustify(inc_header, inc_header_width + 3))
        )

####################

def simpleStats(category, use_header = False):
    if checkCatField():
        catpay_key = category + 'payamt'
        catdep_key = category + 'depamt'
        if not catpay_key in my.catvalues_[-1] or not catdep_key in my.catvalues_[-1]:
            catpay_key = 'payamt'
            catdep_key = 'depamt'
        cat_header_width = core.main.width_[-1][my.catfield_[-1]]
        dec_header = core.main.headers_[-1][my.decfield_[-1]]
        dec_header_width = core.main.width_[-1][my.decfield_[-1]]
        catpay_currency = currency(my.catvalues_[-1][catpay_key])
        inc_header = core.main.headers_[-1][my.incfield_[-1]]
        inc_header_width = core.main.width_[-1][my.incfield_[-1]]
        catdep_currency = currency(my.catvalues_[-1][catdep_key])
        if not use_header:
            if core.main.output_[-1]:
                printLine('{0} :: {1}: {2}  {3}: {4}'.format(
                    rjustify(category, cat_header_width),
                    rjustify(dec_header, dec_header_width),
                    rjustify(catpay_currency, dec_header_width + 3),
                    rjustify(inc_header, inc_header_width),
                    rjustify(catdep_currency, inc_header_width + 3))
                )
        else:
            if core.main.output_[-1]:
                printLine('{0} | {1}  {2}'.format(
                    rjustify(category, cat_header_width),
                    rjustify(catpay_currency, dec_header_width + 3),
                    rjustify(catdep_currency, inc_header_width + 3))
                )

####################

def moreStats(category):
    if checkCatField():
        min_in_key = category + 'min-in'
        max_in_key = category + 'max-in'
        num_in_key = category + 'num-in'
        sum_in_key = category + 'sum-in'
        min_out_key = category + 'min-out'
        max_out_key = category + 'max-out'
        num_out_key = category + 'num-out'
        sum_out_key = category + 'sum-out'
        general = False
        if not min_in_key in my.statvalues_[-1] or not max_in_key in my.statvalues_[-1] or not num_in_key in my.statvalues_[-1] or not sum_in_key in my.statvalues_[-1] or not min_out_key in my.statvalues_[-1] or not max_out_key in my.statvalues_[-1] or not num_out_key in my.statvalues_[-1] or not sum_out_key in my.statvalues_[-1]:
            general = True
            min_in_key = 'min-in'
            max_in_key = 'max-in'
            num_in_key = 'num-in'
            sum_in_key = 'sum-in'
            min_out_key = 'min-out'
            max_out_key = 'max-out'
            num_out_key = 'num-out'
            sum_out_key = 'sum-out'
        start = my.statvalues_[-1]['init']
        finish = my.fulbal_[-1]
        change = round(100 * (finish - start) / start)
        change_str = 'decrease' if change < 0 else 'increase'
        change_str = 'change' if change == 0 else change_str
        min_in = my.statvalues_[-1][min_in_key] if my.statvalues_[-1][min_in_key] != stats_max else 0
        num_in = my.statvalues_[-1][num_in_key]
        sum_in = my.statvalues_[-1][sum_in_key]
        avg_in = sum_in / num_in if num_in > 0 else 0
        max_in = my.statvalues_[-1][max_in_key]
        header_in = core.main.headers_[-1][my.incfield_[-1]]
        width_in = core.main.width_[-1][my.incfield_[-1]]
        min_out = my.statvalues_[-1][min_out_key] if my.statvalues_[-1][min_out_key] != stats_max else 0
        num_out = my.statvalues_[-1][num_out_key]
        sum_out = my.statvalues_[-1][sum_out_key]
        avg_out = sum_out / num_out if num_out > 0 else 0
        max_out = my.statvalues_[-1][max_out_key]
        header_out = core.main.headers_[-1][my.decfield_[-1]]
        width_out = core.main.width_[-1][my.decfield_[-1]]
        if core.main.output_[-1]:
            printLine(f"{category}:")
            printLine('{0} {1}, {2} {3}'.format(currency(sum_out), header_out, currency(sum_in), header_in))
            if general:
                printLine('{0} start, {1} finish, {2}% {3}'.format(currency(start), currency(finish), abs(change), change_str))
            printLine('{0} min / avg / max = {1} / {2} / {3}'.format(ljustify(header_out, width_out),
                rjustify(currency(min_out), width_out), rjustify(currency(avg_out), width_out), rjustify(currency(max_out), width_out))
            )
            printLine('{0} min / avg / max = {1} / {2} / {3}'.format(ljustify(header_in, width_in),
                rjustify(currency(min_in), width_in), rjustify(currency(avg_in), width_in), rjustify(currency(max_in), width_in))
            )
            printLine()

def checkCatField():
    if my.catfield_[-1] == None:
        errorMessage('Cannot run &stats when catfield is not set.')
        return False
    return True

################################################################################
# add command-line options just for this plugin
################################################################################

def parseOption(option, parameter):
    # result[0] = known/unknown
    # result[1] = skip next word (option parameter)
    result = [False, False]
    if parameter == None:
        parameter = ''
    if option in ['-oi', '--override-init']:
        parseMyDirective('&init {0}'.format(parameter))
        cli.override_init = True
        result = [True, True]
    return result

################################################################################
# plugin-specific parsing
################################################################################

def pluginMain(line):
    out = preParse(line)
    if core.main.header_mode_:
        if core.main.output_[-1] and out != None:
            printLine(out)
        core.main.header_mode_ = False
        return
    payamt = 0.0
    depamt = 0.0
    if my.decfield_[-1] != None:
        payamt = core.main.elements_[my.decfield_[-1]]
        payamt = re.sub('^\d\.-', '', payamt)
        if payamt.strip() == '':
            payamt = 0.0
    else:
        errorMessage('Decrement field is not set.')
    if my.incfield_[-1] != None:
        depamt = core.main.elements_[my.incfield_[-1]]
        depamt = re.sub('^\d\.-', '', depamt)
        if depamt.strip() == '':
            depamt = 0.0
    else:
        errorMessage('Increment field is not set.')
    try:
        # calculate running balance
        my.fulbal_[-1] -= float(payamt)
        my.fulbal_[-1] += float(depamt)

        # record general category values
        if not 'payamt' in my.catvalues_[-1]: my.catvalues_[-1]['payamt'] = 0.0
        my.catvalues_[-1]['payamt'] += float(payamt)
        if not 'depamt' in my.catvalues_[-1]: my.catvalues_[-1]['depamt'] = 0.0
        my.catvalues_[-1]['depamt'] += float(depamt)

        # record general stats values
        if not 'min-in' in my.statvalues_[-1]: my.statvalues_[-1]['min-in'] = stats_max
        if float(depamt) < my.statvalues_[-1]['min-in'] and float(payamt) == 0.0:
            my.statvalues_[-1]['min-in'] = float(depamt)
        if not 'max-in' in my.statvalues_[-1]: my.statvalues_[-1]['max-in'] = stats_min
        if float(depamt) > my.statvalues_[-1]['max-in']:
            my.statvalues_[-1]['max-in'] = float(depamt)
        if not 'num-in' in my.statvalues_[-1]: my.statvalues_[-1]['num-in'] = 0
        if not 'sum-in' in my.statvalues_[-1]: my.statvalues_[-1]['sum-in'] = 0
        if float(depamt) > 0:
            my.statvalues_[-1]['num-in'] += 1
            my.statvalues_[-1]['sum-in'] += float(depamt)
        if not 'min-out' in my.statvalues_[-1]: my.statvalues_[-1]['min-out'] = stats_max
        if float(payamt) < my.statvalues_[-1]['min-out'] and float(depamt) == 0.0:
            my.statvalues_[-1]['min-out'] = float(payamt)
        if not 'max-out' in my.statvalues_[-1]: my.statvalues_[-1]['max-out'] = stats_min
        if float(payamt) > my.statvalues_[-1]['max-out']:
            my.statvalues_[-1]['max-out'] = float(payamt)
        if not 'num-out' in my.statvalues_[-1]: my.statvalues_[-1]['num-out'] = 0
        if not 'sum-out' in my.statvalues_[-1]: my.statvalues_[-1]['sum-out'] = 0
        if float(payamt) > 0:
            my.statvalues_[-1]['num-out'] += 1
            my.statvalues_[-1]['sum-out'] += float(payamt)

        # record specific category values
        if my.clrfield_[-1] != None and core.main.elements_[my.clrfield_[-1]] != ' ':
            my.clrbal_[-1] -= float(payamt)
            my.clrbal_[-1] += float(depamt)
        if my.catfield_[-1] != None and core.main.elements_[my.catfield_[-1]] != ' ':
            for catkey in core.main.elements_[my.catfield_[-1]].split():
                catpay_key = catkey + 'payamt'
                catdep_key = catkey + 'depamt'
                if not catpay_key in my.catvalues_[-1]: my.catvalues_[-1][catpay_key] = 0.0
                my.catvalues_[-1][catpay_key] += float(payamt)
                if not catdep_key in my.catvalues_[-1]: my.catvalues_[-1][catdep_key] = 0.0
                my.catvalues_[-1][catdep_key] += float(depamt)

        # record specific stats values
        if my.catfield_[-1] != None and core.main.elements_[my.catfield_[-1]] != ' ':
            for statkey in core.main.elements_[my.catfield_[-1]].split():
                min_in_key = statkey + 'min-in'
                max_in_key = statkey + 'max-in'
                num_in_key = statkey + 'num-in'
                sum_in_key = statkey + 'sum-in'
                if not min_in_key in my.statvalues_[-1]: my.statvalues_[-1][min_in_key] = 9999999.0
                if float(depamt) < my.statvalues_[-1][min_in_key] and float(payamt) == 0.0:
                    my.statvalues_[-1][min_in_key] = float(depamt)
                if not max_in_key in my.statvalues_[-1]: my.statvalues_[-1][max_in_key] = 0.0
                if float(depamt) > my.statvalues_[-1][max_in_key]:
                    my.statvalues_[-1][max_in_key] = float(depamt)
                if not num_in_key in my.statvalues_[-1]: my.statvalues_[-1][num_in_key] = 0
                if not sum_in_key in my.statvalues_[-1]: my.statvalues_[-1][sum_in_key] = 0
                if float(depamt) > 0:
                    my.statvalues_[-1][num_in_key] += 1
                    my.statvalues_[-1][sum_in_key] += float(depamt)
                min_out_key = statkey + 'min-out'
                max_out_key = statkey + 'max-out'
                num_out_key = statkey + 'num-out'
                sum_out_key = statkey + 'sum-out'
                if not min_out_key in my.statvalues_[-1]: my.statvalues_[-1][min_out_key] = 9999999.0
                if float(payamt) < my.statvalues_[-1][min_out_key] and float(depamt) == 0.0:
                    my.statvalues_[-1][min_out_key] = float(payamt)
                if not max_out_key in my.statvalues_[-1]: my.statvalues_[-1][max_out_key] = 0.0
                if float(payamt) > my.statvalues_[-1][max_out_key]:
                    my.statvalues_[-1][max_out_key] = float(payamt)
                if not num_out_key in my.statvalues_[-1]: my.statvalues_[-1][num_out_key] = 0
                if not sum_out_key in my.statvalues_[-1]: my.statvalues_[-1][sum_out_key] = 0
                if float(payamt) > 0:
                    my.statvalues_[-1][num_out_key] += 1
                    my.statvalues_[-1][sum_out_key] += float(payamt)

    except ValueError:
        pass

    if core.main.output_[-1]:
        fulbal = '{:8.2f}'.format(my.fulbal_[-1])
        clrbal = '{:8.2f}'.format(my.clrbal_[-1])
        if len(core.main.formats_[-1]) == len(core.main.elements_) + 2:
            fulbal_index = len(core.main.elements_)
            clrbal_index = len(core.main.elements_) + 1
            fulbal = formatElementByValue(fulbal_index, my.fulbal_[-1])
            clrbal = formatElementByValue(clrbal_index, my.clrbal_[-1])
        printLine(f"{out}{fulbal}{clrbal}")

####################
# start here
####################

def parseLine(line):
    if isDirective(line):
        parseMyDirective(line)
    else:
        pluginMain(line)
