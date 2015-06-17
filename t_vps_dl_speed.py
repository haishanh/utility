#!/usr/bin/env python
# -*- coding: utf-8 -*-

# VPS download speed test (only Digital Ocean currently)
# by haishanh


import subprocess
import re
import signal

def sig_handler(signum, frame):
    # if downloading is break in middle, we need to cleanup the wget intermidiate file 
    global file_to_be_removed
    x = subprocess.Popen('ls -ct ' + file_to_be_removed + '*', shell = True, stdout = subprocess.PIPE)
    f_l = x.stdout.read()
    if f_l:
        f2rm = f_l.split('\n')[0]
        print("file to be removed is: %s" % (f2rm))
        subprocess.call('rm -rf ' + f2rm, shell = True)
    exit(0)

signal.signal(signal.SIGINT, sig_handler)

class cmd():
    def __init__(self):
        self.out = ''
        self.err = ''
        self.status = 1
    def runcmd(self, c):
        c += ' && echo -e "\nstatus => ${?}"'
        x = subprocess.Popen(c, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        x.wait()
        self.out = x.stdout.read() 
        self.err = x.stderr.read() 
        i = re.search(r'^status => (\d)', self.out, re.MULTILINE)
        if i and i.group(1):
            self.status = int(i.group(1))
        else:
            self.status = 1
    def get_out(self):
        return self.out
    def get_err(self):
        return self.err
    def get_status(self):
        return self.status

def is_wget_present(c):
    c.runcmd('which wget')
    if c.get_status() != 0:
        print('wget not found, you may need to install it first\n')
        exit(1)

def prt_result(d, prefix):
    '''d is a dictionary contains the result'''
    for i in d.keys():
        fmt = '%70.70s: %s'
        dot = '.' * 70
        print(fmt % ( prefix + ' ' + i + dot, d[i]))

def t_do(c):
    '''test download speed of different sites of Digital Ocean'''
    # do_sites= ('nyc1', 'nyc2', 'nyc3', 'ams1', 'ams2', 'ams3', 'sfo1', 'sgp1', 'lon1', 'fra1')
    do_sites= ('sfo1', 'sgp1')
    do_speed = {}
    for site in do_sites:
        do_speed[site] = ''
        url = 'http://speedtest-' + site + \
              '.digitalocean.com/10mb.test'
        # print(url)
        global file_to_be_removed
        file_to_be_removed = url.split('/')[-1]
        print("running wget 10mb.test for Digital Ocean site:  %s..." % (site))
        c.runcmd('wget' + ' ' + url)
        date_re = r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}'
        # wget statics is printed in *stderr*
        # 2015-06-06 17:00:44 (2.40 MB/s) - 'abiword-3.0.1-2-i686.pkg.tar.xz.2' saved [5159840/5159840]
        result = re.search(date_re + r'\s' +r'\((\d+\.?\d*\s*[GMK]B/s)\)\s*-\s*\'(.*)\'\s*saved', c.get_err(), re.MULTILINE)
        if result and result.group(1):
            do_speed[site] = result.group(1)
        if result and result.group(2):
            f2rm = result.group(2)
            s = 'rm -rf' + ' ' + f2rm
            subprocess.call(s, shell=True)
    prt_result(do_speed, 'Digital Ocean')

def test(c):
    c.runcmd('ls -l')
    print('the output is:\n%s' % (c.get_out()) )
    print('\nthe status is:\n%s' % (c.get_status()) )
    print('-' * 60)
    c.runcmd('who')
    print('the output is:\n%s' % (c.get_out()) )
    print('\nthe status is:\n%s' % (c.get_status()) )
    print('-' * 60)
    c.runcmd('sleep 10 && echo "Done"')
    print('the output is:\n%s' % (c.get_out()) )
    print('\nthe status is:\n%s' % (c.get_status()) )

if __name__ == '__main__':
    c = cmd()
    # test(c)
    is_wget_present(c)
    t_do(c)
