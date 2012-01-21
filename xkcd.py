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

XKCD_IP='72.26.203.99'
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
            return 'http://' + XKCD_IP + '/{0}/info.0.json'.format(num)
        except AttributeError:
            return 'http://' + XKCD_IP + '/%d/info.0.json' % num
    else:
        return 'http://' + XKCD_IP + '/info.0.json'


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
        for i in filter((lambda i: i or False), meta_labels.keys()):
            file.write(TEMPLATES['entry'].substitute({'label': meta_labels[i],
                'value': cgi.escape(str(data[i], quote=True))}))
        file.write(TEMPLATES['tail'].substitute(data))
        file.close()
    else:
        file = open('%d.html' % num, 'w')
        file.write((TEMPLATES['head'].substitute(data)).encode('utf-8'))
        for i in filter((lambda i: i or False), meta_labels.keys()):
            file.write((TEMPLATES['entry'].substitute({'label': meta_labels[i],
              'value': cgi.escape(str(data[i], quote=True))})).encode('utf-8'))
        file.write((TEMPLATES['tail'].substitute(data)).encode('utf-8'))
        file.close()

    image = uopen(data['img'])
    try:
        img = open('{0}.png'.format(num), 'wb')
    except AttributeError:
        img = open('%d.png' % num, 'wb')
    img.write(image.read())

import os.path

def prerequisites(path = None):
    # Make sure the target directory exists or create it
    os.chdir(os.path.dirname(__file__))
    if not out_dir:
        path = os.path.join('..', 'xkcd')
    if not os.path.exists(path) or (os.path.exists(path) and not os.path.isdir(path)):
    try:
        os.makedirs(path)
    except os.error:
        print ("The directory to save xkcd to doesn't exist and I couldn't create it, %s" % path)
        exit()
    os.chdir(path)
    # Get latest comic number
    return get_json(0)['num']


def download_current(args):
    download(prerequisites(args.out_dir))


def download_archive(args):
    num = prerequisites(args.out_dir)
    for i in range(1, num+1):
        if i != 404:
        print("Downloading comic #%d" % i)
        download(i, args.out_dir)


def download_number(args):
    if args.index == 404 or args.index < 0 or
            args.index > prerequisites(args.out_dir):
        print("Comic with this ID doesn't exist")
    else:
        download(args.index)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Downloads xkcd comics, filtering and reformatting them.')
    parser.add_argument('-o', help="Output to the specified directory,
        creating it if it doesn't exist", dest=out_dir)

    comm_parser = parser.add_subparsers(title='command',
        description = 'the selection method')
    all_parser = comm_parser.add_parser('all', help = 'Download entire archive')
    all_parser.set_defaults(func=download_archive)
    current_parser = comm_parser.add_parser('current',
        help = 'Download the current comic (put this in your crontab!)')
    current_parser.set_defaults(func=download_current)
    comic_parser = comic_parser.add_parser('comic',
        help = 'Download the specified comic number.')
    comic_parser.set_defaults(func=download_number)

    args = parser.parse_args()
    args.func(args)

def main():
    parse_args()

if __name__ == "__main__":
    main()
