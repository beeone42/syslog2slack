#!/usr/bin/env python

import os
import time, datetime
import errno
import stat
import sys
import json
import re
import urllib

CONFIG_FILE = 'config.json'
BUF = 1024
SEEN = []

def open_and_load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print "File [%s] doesn't exist, aborting." % (CONFIG_FILE)
        sys.exit(1)

def load_seen():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as config_file:
            return json.loads(config_file.read())
    else:
        print "File [%s] doesn't exist, aborting." % (CONFIG_FILE)
        sys.exit(1)

def tail(fname, n):
    if (n <= 0):
        raise ValueError('tail: invalid number %r' % n)
    with open(fname, 'rb') as fp:
        data = ''
        NL = '\n'
        size = os.fstat(fp.fileno()).st_size
        nb = -1
        pos = 0
        while (pos >= 0):
            pos = size + (BUF * nb)
            if (pos > 0):
                fp.seek(pos)
            else:
                fp.seek(0)
            data = fp.read(BUF) + data
            nb = nb - 1
            if (data.count(NL) > n):
                return data.splitlines()[-n:]
    return data.splitlines()

def date(format = '%Y-%m-%d %H:%M:%S'):
    d = datetime.datetime.now()
    return d.strftime(format)

def post2slack(config, txt):
    f = { 'token': config['slack-token'],
          'channel': config['slack-channel'],
          'as_user': 'true',
          'text': date() + ' :: ' + txt }
    url = 'https://slack.com/api/chat.postMessage?' + urllib.urlencode(f)
    urllib.urlopen(url)

if __name__ == "__main__":
    config = open_and_load_config()
    while True:
        for f in config['fname']:
            for l in tail(f, config['nb-lines-back']):
                for t in config['tokens']:
                    m = re.search(t, l)
                    if (m):
                        if l not in SEEN:
                            SEEN.append(l)
                            txt = config['prefix'] + ': ' + ' '.join(m.groups())
                            print txt
                            post2slack(config, txt)
        time.sleep(config['sleep-time'])
                
