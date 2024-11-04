#!/usr/bin/env python3

################################################################################
#
# Crunchy Report Generator
#
# Crunch Really Useful Numbers Coded Hackishly
#
# Banking plugin
#
# Copyright (c) 2000, 2022, 2023, 2024 Andy Warmack
# This file is part of Crunchy Report Generator, licensed under the MIT License.
# See the LICENSE file in the project root for more information.
################################################################################

import re

import core
from core_functions import format_element_by_value, ljustify, rjustify, currency, pre_parse, print_line

def identify():
    return 'banking'

class My():
    fulbal_ = []
    clrbal_ = []
    catfield_ = []
    clrfield_ = []
    incfield_ = []
    decfield_ = []
    catvalues_ = []
    statvalues_ = []

def reset():
    My.fulbal_ = [0.0]
    My.clrbal_ = [0.0]
    My.catfield_ = [None]
    My.clrfield_ = [None]
    My.incfield_ = [None]
    My.decfield_ = [None]
    My.catvalues_ = [{}]
    My.statvalues_ = [{}]

class Cli():
    override_init = False

reset()

def get_env():
    return [
        My.fulbal_,
        My.clrbal_,
        My.catfield_,
        My.clrfield_,
        My.incfield_,
        My.decfield_,
        My.catvalues_,
        My.statvalues_
    ]

# min-max boundaries for stats
STATS_MIN = 0.0
STATS_MAX = 9999999.0

################################################################################
# parse plugin-specific directives, but pre-parse for core directives first
################################################################################

def parse_my_directive(line):
    p = core.Main.parser()
    p.pre_parse_directive(line)
    if p.done:
        return
    argtrim = p.argtrim
    cmd = p.cmd
    options = p.options

    ####################

    if cmd == 'init':
        if argtrim:
            if not Cli.override_init:
                My.fulbal_[-1] = float(argtrim)
                My.clrbal_[-1] = My.fulbal_[-1]
                My.statvalues_[-1]['init'] = My.fulbal_[-1]
                core.Main.msg.info_message(f"Initializing balance to {currency(My.fulbal_[-1])}.")
            else:
                core.Main.msg.info_message('Overriding &init directive.')
        else:
            p.invalid_usage('&init <float>')

    ####################

    elif cmd == 'set':
        show_usage = False
        if argtrim:
            parts = argtrim.split()
            if len(parts) > 1:
                if parts[0] == 'catfield':
                    My.catfield_[-1] = int(parts[1])
                    core.Main.msg.info_message(f"Setting category field to {str(My.catfield_[-1])}.")
                elif parts[0] == 'clrfield':
                    My.clrfield_[-1] = int(parts[1])
                    core.Main.msg.info_message(f"Setting clear field to {str(My.clrfield_[-1])}.")
                elif parts[0] == 'decfield':
                    My.decfield_[-1] = int(parts[1])
                    core.Main.msg.info_message(f"Setting decrement field to {str(My.decfield_[-1])}.")
                elif parts[0] == 'incfield':
                    My.incfield_[-1] = int(parts[1])
                    core.Main.msg.info_message(f"Setting increment field to {str(My.incfield_[-1])}.")
                else:
                    show_usage = True
            else:
                show_usage = True
        else:
            show_usage = True
        if show_usage:
            p.invalid_usage('&set [ catfield <int> | clrfield <int> | decfield <int> | incfield <int> ]')

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
                core.Main.parser.unrecognized_option(option)
        if init:
            My.catvalues_ = [{}]
            My.statvalues_ = [{}]
            core.Main.msg.info_message('Stats initialized.')
        elif simple:
            if not argtrim:
                simple_stats('All')
            elif not ' ' in argtrim:
                simple_stats(argtrim)
            else:
                simple_stats_header()
                for category in argtrim.split():
                    simple_stats(category, True)
                if core.Main.output_[-1]:
                    print_line()
        else:
            if not argtrim:
                more_stats('All')
            elif not ' ' in argtrim:
                more_stats(argtrim)
            else:
                for category in argtrim.split():
                    more_stats(category)

    ####################

    else:
        p.invalid_directive()

################################################################################
# display banking stats in simple and complex formats
################################################################################

def simple_stats_header():
    cat_header_width = core.Main.width_[-1][My.catfield_[-1]]
    dec_header = core.Main.headers_[-1][My.decfield_[-1]]
    dec_header_width = core.Main.width_[-1][My.decfield_[-1]]
    inc_header = core.Main.headers_[-1][My.incfield_[-1]]
    inc_header_width = core.Main.width_[-1][My.incfield_[-1]]
    if core.Main.output_[-1]:
        cat_header_rj = rjustify('', cat_header_width + 2)
        dec_header_rj = rjustify(dec_header, dec_header_width + 3)
        inc_header_rj = rjustify(inc_header, inc_header_width + 3)
        print_line(f"{cat_header_rj} {dec_header_rj}  {inc_header_rj}")

####################

def simple_stats(category, use_header = False):
    if check_cat_field():
        catpay_key = category + 'payamt'
        catdep_key = category + 'depamt'
        if not catpay_key in My.catvalues_[-1] or not catdep_key in My.catvalues_[-1]:
            catpay_key = 'payamt'
            catdep_key = 'depamt'
        cat_header_width = core.Main.width_[-1][My.catfield_[-1]]
        dec_header = core.Main.headers_[-1][My.decfield_[-1]]
        dec_header_width = core.Main.width_[-1][My.decfield_[-1]]
        catpay_currency = currency(My.catvalues_[-1][catpay_key])
        inc_header = core.Main.headers_[-1][My.incfield_[-1]]
        inc_header_width = core.Main.width_[-1][My.incfield_[-1]]
        catdep_currency = currency(My.catvalues_[-1][catdep_key])
        if not use_header:
            if core.Main.output_[-1]:
                category_rj = rjustify(category, cat_header_width)
                dec_header_rj = rjustify(dec_header, dec_header_width)
                catpay_currency_rj = rjustify(catpay_currency, dec_header_width + 3)
                inc_header_rj = rjustify(inc_header, inc_header_width)
                catdep_currency_rj = rjustify(catdep_currency, inc_header_width + 3)
                print_line(f"{category_rj} :: {dec_header_rj}: {catpay_currency_rj}  {inc_header_rj}: {catdep_currency_rj}")
        else:
            if core.Main.output_[-1]:
                category_rj = rjustify(category, cat_header_width)
                catpay_currency_rj = rjustify(catpay_currency, dec_header_width + 3)
                catdep_currency_rj = rjustify(catdep_currency, inc_header_width + 3)
                print_line(f"{category_rj} | {catpay_currency_rj}  {catdep_currency_rj}")

####################

def more_stats(category):
    if check_cat_field():
        min_in_key = category + 'min-in'
        max_in_key = category + 'max-in'
        num_in_key = category + 'num-in'
        sum_in_key = category + 'sum-in'
        min_out_key = category + 'min-out'
        max_out_key = category + 'max-out'
        num_out_key = category + 'num-out'
        sum_out_key = category + 'sum-out'
        general = False
        keys = [min_in_key, max_in_key, num_in_key, sum_in_key, min_out_key, max_out_key, num_out_key, sum_out_key]
        if not all (key in My.statvalues_[-1] for key in keys):
            general = True
            min_in_key = 'min-in'
            max_in_key = 'max-in'
            num_in_key = 'num-in'
            sum_in_key = 'sum-in'
            min_out_key = 'min-out'
            max_out_key = 'max-out'
            num_out_key = 'num-out'
            sum_out_key = 'sum-out'
        start = My.statvalues_[-1]['init']
        finish = My.fulbal_[-1]
        change = round(100 * (finish - start) / start)
        change_str = 'decrease' if change < 0 else 'increase'
        change_str = 'change' if change == 0 else change_str
        min_in = My.statvalues_[-1][min_in_key] if My.statvalues_[-1][min_in_key] != STATS_MAX else 0
        num_in = My.statvalues_[-1][num_in_key]
        sum_in = My.statvalues_[-1][sum_in_key]
        avg_in = sum_in / num_in if num_in > 0 else 0
        max_in = My.statvalues_[-1][max_in_key]
        header_in = core.Main.headers_[-1][My.incfield_[-1]]
        width_in = core.Main.width_[-1][My.incfield_[-1]]
        min_out = My.statvalues_[-1][min_out_key] if My.statvalues_[-1][min_out_key] != STATS_MAX else 0
        num_out = My.statvalues_[-1][num_out_key]
        sum_out = My.statvalues_[-1][sum_out_key]
        avg_out = sum_out / num_out if num_out > 0 else 0
        max_out = My.statvalues_[-1][max_out_key]
        header_out = core.Main.headers_[-1][My.decfield_[-1]]
        width_out = core.Main.width_[-1][My.decfield_[-1]]
        if core.Main.output_[-1]:
            print_line(f"{category}:")
            print_line(f"{currency(sum_out)} {header_out}, {currency(sum_in)} {header_in}")
            if general:
                print_line(f"{currency(start)} start, {currency(finish)} finish, {abs(change)}% {change_str}")
            header_out_lj = ljustify(header_out, width_out)
            min_out_rj = rjustify(currency(min_out), width_out)
            avg_out_rj = rjustify(currency(avg_out), width_out)
            max_out_rj = rjustify(currency(max_out), width_out)
            print_line(f"{header_out_lj} min / avg / max = {min_out_rj} / {avg_out_rj} / {max_out_rj}")
            header_in_lj = ljustify(header_in, width_in)
            min_in_rj = rjustify(currency(min_in), width_in)
            avg_in_rj = rjustify(currency(avg_in), width_in)
            max_in_rj = rjustify(currency(max_in), width_in)
            print_line(f"{header_in_lj} min / avg / max = {min_in_rj} / {avg_in_rj} / {max_in_rj}")
            print_line()

def check_cat_field():
    if My.catfield_[-1] is None:
        core.Main.msg.error_message('Cannot run &stats when catfield is not set.')
        return False
    return True

################################################################################
# add command-line options just for this plugin
################################################################################

def parse_option(option, parameter):
    # result[0] = known/unknown
    # result[1] = skip next word (option parameter)
    result = [False, False]
    if parameter is None:
        parameter = ''
    if option in ['-oi', '--override-init']:
        parse_my_directive(f"&init {parameter}")
        Cli.override_init = True
        result = [True, True]
    return result

################################################################################
# plugin-specific parsing
################################################################################

def plugin_main(line):
    out = pre_parse(line)
    if out is None:
        return

    if core.Main.header_mode_:
        if core.Main.output_[-1] and out is not None:
            print_line(out)
        core.Main.header_mode_ = False
        return
    payamt = 0.0
    depamt = 0.0
    if My.decfield_[-1] is not None:
        payamt = core.Main.elements_[My.decfield_[-1]]
        payamt = re.sub(r'^\d\.-', '', payamt)
        if payamt.strip() == '':
            payamt = 0.0
    else:
        core.Main.msg.error_message('Decrement field is not set.')
    if My.incfield_[-1] is not None:
        depamt = core.Main.elements_[My.incfield_[-1]]
        depamt = re.sub(r'^\d\.-', '', depamt)
        if depamt.strip() == '':
            depamt = 0.0
    else:
        core.Main.msg.error_message('Increment field is not set.')
    try:
        # calculate running balance
        My.fulbal_[-1] -= float(payamt)
        My.fulbal_[-1] += float(depamt)

        # record general category values
        if not 'payamt' in My.catvalues_[-1]:
            My.catvalues_[-1]['payamt'] = 0.0
        My.catvalues_[-1]['payamt'] += float(payamt)
        if not 'depamt' in My.catvalues_[-1]:
            My.catvalues_[-1]['depamt'] = 0.0
        My.catvalues_[-1]['depamt'] += float(depamt)

        # record general stats values
        if not 'min-in' in My.statvalues_[-1]:
            My.statvalues_[-1]['min-in'] = STATS_MAX
        if float(depamt) < My.statvalues_[-1]['min-in'] and float(payamt) == 0.0:
            My.statvalues_[-1]['min-in'] = float(depamt)
        if not 'max-in' in My.statvalues_[-1]:
            My.statvalues_[-1]['max-in'] = STATS_MIN
        if float(depamt) > My.statvalues_[-1]['max-in']:
            My.statvalues_[-1]['max-in'] = float(depamt)
        if not 'num-in' in My.statvalues_[-1]:
            My.statvalues_[-1]['num-in'] = 0
        if not 'sum-in' in My.statvalues_[-1]:
            My.statvalues_[-1]['sum-in'] = 0
        if float(depamt) > 0:
            My.statvalues_[-1]['num-in'] += 1
            My.statvalues_[-1]['sum-in'] += float(depamt)
        if not 'min-out' in My.statvalues_[-1]:
            My.statvalues_[-1]['min-out'] = STATS_MAX
        if float(payamt) < My.statvalues_[-1]['min-out'] and float(depamt) == 0.0:
            My.statvalues_[-1]['min-out'] = float(payamt)
        if not 'max-out' in My.statvalues_[-1]:
            My.statvalues_[-1]['max-out'] = STATS_MIN
        if float(payamt) > My.statvalues_[-1]['max-out']:
            My.statvalues_[-1]['max-out'] = float(payamt)
        if not 'num-out' in My.statvalues_[-1]:
            My.statvalues_[-1]['num-out'] = 0
        if not 'sum-out' in My.statvalues_[-1]:
            My.statvalues_[-1]['sum-out'] = 0
        if float(payamt) > 0:
            My.statvalues_[-1]['num-out'] += 1
            My.statvalues_[-1]['sum-out'] += float(payamt)

        # record specific category values
        if My.clrfield_[-1] is not None and core.Main.elements_[My.clrfield_[-1]] != ' ':
            My.clrbal_[-1] -= float(payamt)
            My.clrbal_[-1] += float(depamt)
        if My.catfield_[-1] is not None and core.Main.elements_[My.catfield_[-1]] != ' ':
            for catkey in core.Main.elements_[My.catfield_[-1]].split():
                catpay_key = catkey + 'payamt'
                catdep_key = catkey + 'depamt'
                if not catpay_key in My.catvalues_[-1]:
                    My.catvalues_[-1][catpay_key] = 0.0
                My.catvalues_[-1][catpay_key] += float(payamt)
                if not catdep_key in My.catvalues_[-1]:
                    My.catvalues_[-1][catdep_key] = 0.0
                My.catvalues_[-1][catdep_key] += float(depamt)

        # record specific stats values
        if My.catfield_[-1] is not None and core.Main.elements_[My.catfield_[-1]] != ' ':
            for statkey in core.Main.elements_[My.catfield_[-1]].split():
                min_in_key = statkey + 'min-in'
                max_in_key = statkey + 'max-in'
                num_in_key = statkey + 'num-in'
                sum_in_key = statkey + 'sum-in'
                if not min_in_key in My.statvalues_[-1]:
                    My.statvalues_[-1][min_in_key] = 9999999.0
                if float(depamt) < My.statvalues_[-1][min_in_key] and float(payamt) == 0.0:
                    My.statvalues_[-1][min_in_key] = float(depamt)
                if not max_in_key in My.statvalues_[-1]:
                    My.statvalues_[-1][max_in_key] = 0.0
                if float(depamt) > My.statvalues_[-1][max_in_key]:
                    My.statvalues_[-1][max_in_key] = float(depamt)
                if not num_in_key in My.statvalues_[-1]:
                    My.statvalues_[-1][num_in_key] = 0
                if not sum_in_key in My.statvalues_[-1]:
                    My.statvalues_[-1][sum_in_key] = 0
                if float(depamt) > 0:
                    My.statvalues_[-1][num_in_key] += 1
                    My.statvalues_[-1][sum_in_key] += float(depamt)
                min_out_key = statkey + 'min-out'
                max_out_key = statkey + 'max-out'
                num_out_key = statkey + 'num-out'
                sum_out_key = statkey + 'sum-out'
                if not min_out_key in My.statvalues_[-1]:
                    My.statvalues_[-1][min_out_key] = 9999999.0
                if float(payamt) < My.statvalues_[-1][min_out_key] and float(depamt) == 0.0:
                    My.statvalues_[-1][min_out_key] = float(payamt)
                if not max_out_key in My.statvalues_[-1]:
                    My.statvalues_[-1][max_out_key] = 0.0
                if float(payamt) > My.statvalues_[-1][max_out_key]:
                    My.statvalues_[-1][max_out_key] = float(payamt)
                if not num_out_key in My.statvalues_[-1]:
                    My.statvalues_[-1][num_out_key] = 0
                if not sum_out_key in My.statvalues_[-1]:
                    My.statvalues_[-1][sum_out_key] = 0
                if float(payamt) > 0:
                    My.statvalues_[-1][num_out_key] += 1
                    My.statvalues_[-1][sum_out_key] += float(payamt)

    except ValueError:
        pass

    if core.Main.output_[-1]:
        fulbal = f"{My.fulbal_[-1]:8.2f}"
        clrbal = f"{My.clrbal_[-1]:8.2f}"
        if len(core.Main.formats_[-1]) == len(core.Main.elements_) + 2:
            fulbal_index = len(core.Main.elements_)
            clrbal_index = len(core.Main.elements_) + 1
            fulbal = format_element_by_value(fulbal_index, My.fulbal_[-1])
            clrbal = format_element_by_value(clrbal_index, My.clrbal_[-1])
        print_line(f"{out}{fulbal}{clrbal}")

####################
# start here
####################

def parse_line(line):
    if core.Main.parser().is_directive(line):
        parse_my_directive(line)
    else:
        plugin_main(line)
