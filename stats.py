#!/usr/bin/env python3

"""
Python script for gathering simple host information:
- current RAM usage;
- current CPU usage;
- current number of processes running.
"""

import argparse
import datetime
import logging
import os
import time
import sys

from collections import OrderedDict


def parse_args():
    """Parse and return script arguments."""
    parser = argparse.ArgumentParser(description='Host stats')

    parser.add_argument('-c', '--cpu', action='store_true', default=False,
                        dest='is_cpu', help='CPU usage')
    parser.add_argument('-m', '--memory', action='store_true', default=False,
                        dest='is_mem', help='Memory usage')
    parser.add_argument('-p', '--processes', action='store_true', default=False,
                        dest='is_proc', help='Processes quantity')
    parser.add_argument('-f', '--file', action='store', dest='filename',
                        help='Dump stats to file')

    return parser.parse_args()


def get_cpu_usage():
    """Calculate and return current CPU utilization."""
    last_idle = last_total = 0

    with open('/proc/stat') as file:
        for i in range(2):
            fields = [float(col) for col in file.readline().strip().split()[1:]]
            idle, total = fields[3], sum(fields)
            idle_delta, total_delta = idle - last_idle, total - last_total
            last_idle, last_total = idle, total
            file.seek(0)
            time.sleep(0.5)

    cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)

    return '{0:.1f}%'.format(cpu_usage)


def get_memory_usage():
    """Calculate and return current Memory usage."""
    mem_info = {}

    with open('/proc/meminfo') as file:
        for line in file:
            if line.startswith(('MemTotal', 'MemFree', 'Buffers', 'Cached', 'Slab')):
                line_split = line.split()
                mem_info[line_split[0][:-1]] = float(line_split[1])

    used_mem = round((mem_info['MemTotal'] - mem_info['MemFree'] - (
            mem_info['Buffers'] + mem_info['Cached'] + mem_info['Slab'])) / 1024.0)

    return '{0}MB'.format(used_mem)


def get_processes_quantity():
    """Calculate and return processes quantity."""
    return len([val for val in os.listdir('/proc') if val.isdigit()])


def dump_stats(filename, stats_msg):
    """Write stats to a file."""
    filemode = 'a' if os.path.isfile(filename) else 'w'

    with open(filename, filemode) as file:
        file.write('{0}\n'.format(stats_msg))


def main():
    log_level = logging.DEBUG
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(format=log_format, level=log_level,
                        filename='{0}.log'.format(
                            os.path.splitext(os.path.basename(__file__))[0]))
    log = logging.getLogger(__name__)
    stats = OrderedDict()

    log.info('Starting stats collector')
    args = parse_args()

    if not (args.is_cpu or args.is_mem or args.is_proc):
        args.is_cpu = args.is_mem = args.is_proc = True

    if args.is_cpu:
        log.info('Getting CPU usage')
        stats['cpu_usage'] = get_cpu_usage()
        log.debug('CPU usage: %s', stats['cpu_usage'])

    if args.is_mem:
        log.info('Getting Memory usage')
        stats['mem_usage'] = get_memory_usage()
        log.debug('Memory usage: %s', stats['mem_usage'])

    if args.is_proc:
        log.info('Getting Processes quantity')
        stats['proc_quantity'] = get_processes_quantity()
        log.debug('Processes quantity: %s', stats['proc_quantity'])

    stats_msg = '{0} {1}'.format(
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ' '.join("{}:{}".format(key, val) for (key, val) in stats.items()))

    log.info('Printing stats to STDOUT')
    log.debug('Stats: %s', stats_msg)
    print(stats_msg)

    if args.filename:
        log.info('Dumping stats to %s', args.filename)
        dump_stats(args.filename, stats_msg)


if __name__ == '__main__':
    sys.exit(main())
