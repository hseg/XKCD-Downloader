#!/usr/bin/python
# -*- coding: utf-8 -*-
# xkcd Downloader
import sys
from sys import argv

try:
    from urllib.request import urlopen as uopen
    import urllib.request
except:
    from urllib import urlopen as uopen

import string

try:
    import json
except ImportError:
    import simplejson as json

import os
import cgi
import argparse

TEMPLATES={ 'head': string.Template('''<!DOCTYPE html>
<html>
<head>
<title>XKCD: ${safe_title}</title>
</head>
<body>
<h1><a href="${url}">${safe_title}</a></h1>
<table>'''),
'entry': string.Template('<tr><td><b>${label}</b></td><td>${value}</td></tr>'),
'tail': string.Template('''</table>
<a href="${img}"><img src="${num}.png" title="${alt}" /></a>
<p>${alt}</p>
<br/><br/>
<p>${transcript}
</body>
</html>''')}

def get_url(num):
    if(num >= 1):
        try:
            return 'http://www.xkcd.com/{0}/info.0.json'.format(num)
        except AttributeError:
            return 'http://www.xkcd.com/%d/info.0.json' % num
    else:
        return 'http://www.xkcd.com/info.0.json'


def get_json(num):
    url = get_url(num)

    # Download JSON, retrying in case of an error
    while True:
        try:
            comic = uopen(url).read().decode()
            break
        except:
            raise

    # A crutch for a comic json with apparently an error in it
    if num == 971:
        comic = comic.replace("\u00e2\u0080\u0099", "'")

    # Open JSON file
    return json.loads(comic)


def update_meta(meta):
    try:
        meta['date'] = '{0}/{1}/{2}'.format(meta['day'],
            meta['month'], meta['year'])
    except AttributeError:
        meta['date'] = '{%s}/{%s}/{%s}' % (meta['day'],
            meta['month'], meta['year'])
    meta['url'] = meta['img'].rsplit('/', 1)[0] + '/'


def download(num):
    data = get_json(num)

    # Save JSON
    if sys.version_info[0] >= 3:
        json_file = open('{0}.json'.format(num), 'w', encoding='utf-8')
        json_file.write(str(data))
    else:
        json_file = open('%d.json' % num, 'w')
        json_file.write(str(data).encode('utf-8'))

    # Create HTML from template
    update_meta(data)
    meta_labels = {'num': 'Number:', 'date': 'Published:', 'news': 'News:',
                'link': 'Link:'}

    # Write HTML and image to file
    if sys.version_info[0] >= 3:
        file = open('{0}.html'.format(num), 'w', encoding='utf-8')
        file.write(TEMPLATES['head'].substitute(data))
        for i in filter((lambda i: data[i] or False), meta_labels.keys()):
            file.write(TEMPLATES['entry'].substitute({'label': meta_labels[i],
                'value': cgi.escape(str(data[i]), quote=True)}))
        file.write(TEMPLATES['tail'].substitute(data))
        file.close()
    else:
        file = open('%d.html' % num, 'w')
        file.write((TEMPLATES['head'].substitute(data)).encode('utf-8'))
        for i in filter((lambda i: data[i] or False), meta_labels.keys()):
            file.write((TEMPLATES['entry'].substitute({'label': meta_labels[i],
                'value': cgi.escape(str(data[i]), quote=True)})).encode('utf-8'))
        file.write((TEMPLATES['tail'].substitute(data)).encode('utf-8'))
        file.close()

    image = uopen(data['img'])
    try:
        img = open('{0}.png'.format(num), 'wb')
    except AttributeError:
        img = open('%d.png' % num, 'wb')
    img.write(image.read())

def valid_idlist(max):
    return [i for i in range(1,max+1) if not (i == 404)]

import os.path

def prerequisites(path = None):
    # Make sure the target directory exists or create it
    os.chdir(os.path.dirname(__file__))
    if not path:
        path = os.path.join('..', 'xkcd')
    if not os.path.exists(path) or (os.path.exists(path)
        and not os.path.isdir(path)):
        try:
            os.makedirs(path)
        except os.error:
            print ("The directory to save xkcd to doesn't exist\
                and couldn't be created, %s" % path)
            exit()
    os.chdir(path)
    # Get latest comic number
    return get_json(0)['num']

def download_current(args):
    download(prerequisites(args.out_dir))

def download_archive(args):
    for i in valid_idlist(prerequisites(args.out_dir)):
        print("Downloading comic #%d" % i)
        download(i)

def download_number(args):
    if (args.index in valid_idlist(prerequisites(args.out_dir))):
        print("Comic with this ID doesn't exist")
    else:
        download(args.index)

def download_update(args):
    to_download = set(x for x in valid_idlist(prerequisites(args.out_dir))
        if not(os.path.exists("%s.html" % x) or os.path.exists("%s.htm" % x)))
    for i in to_download:
        print("Downloading comic #%d" % i)
        download(i)

def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads xkcd comics, filtering and reformatting them.')
    parser.add_argument('-o', '--out_dir',
      help="Output to the specified directory, (default: .\\xkcd)")

    comm_parser = parser.add_subparsers(title='command',
        description = 'the selection method')

    all_parser = comm_parser.add_parser('all', help = 'Download entire archive')
    all_parser.set_defaults(func=download_archive)

    current_parser = comm_parser.add_parser('current',
        help = 'Download the current comic')
    current_parser.set_defaults(func=download_current)

    comic_parser = comm_parser.add_parser('comic',
        help = 'Download the specified comic number.')
    comic_parser.set_defaults(func=download_number)

    update_parser = comm_parser.add_parser('update', help='Update the archive '
                                + '- put this in your crontab')
    update_parser.set_defaults(func=download_update)

    args = parser.parse_args()
    args.func(args)

def main():
    parse_args()

if __name__ == "__main__":
    main()
