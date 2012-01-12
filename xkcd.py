#!/usr/bin/python
# XKCD Downloader
# Downloads an XKCD comic given the comic number.
# Filters the data and reformats it.

from urllib.request import urlopen as uopen
import string
import urllib.request
import json
import sys
import os

XKCD_IP='72.26.203.99'
TEMPLATES={}

def gen_templates():
    TEMPLATES['head'] = string.Template('''
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>XKCD: ${safe_title}</title>
</head>
<body>
<h1><a href="${url}">${safe_title}</a></h1>
<table>''')
    TEMPLATES['entry'] =
       string.Template('<tr><td><b>${label}</b></td><td>${value}</td></tr>')
    TEMPLATES['tail'] = string.Template('''
</table>
<a href="${img}"><img src="${num}.png" title=${alt} /></a>
<p>${alt}</p>
<br/><br/>
<p>${transcript}
</body>
</html>''')

def get_url(num):
    if(num >= 1):
        return 'http://' + XKCD_IP + '/{0}/info.0.json'.format(num)
    else:
        return 'http://' + XKCD_IP + '/info.0.json'

def get_json(num):
    url = get_url(num)

# Download JSON
    while True:
        try:
            comic = uopen(url).readall().decode()
            break
        except:
            raise

    # Open JSON file
    return json.loads(comic)

def update_meta(meta):
    meta['date'] = '{0}/{1}/{2}'.format(meta['day'], meta['month'], meta['year'])
    meta['url'] = url.rsplit('/', 1)[0] + '/'
                'link': 'Link:'}

def download(num):
    data = get_json(num):

    # Save JSON
    json_file = open('{0}.json'.format(num), 'w', encoding='utf-8')
    json_file.write(str(data))

    # Create HTML from template
    update_meta(data)
    meta_labels = {'num': 'Number:', 'date': 'Published:', 'news': 'News:',
                'link': 'Link:'}

    # Write HTML and image to file
    file = open('{0}.html'.format(num), 'w', encoding='utf-8')
    file.write(head.substitute(data))
    for i in filter((lambda i: i or False), meta_labels.keys()):
        file.write(entry.substitute({'label': meta_labels[i], 'value': data[i]}))
    file.write(tail.substitute(data))

    image = uopen(data['img'])
    img = open('{0}.png'.format(num), 'bw')
    img.write(image.read())

if __name__ == "__main__":
    gen_templates()
    # Get latest comic number
    num = get_json(0)['num']

    os.chdir('..\XKCD')
    for i in xrange(1, num+1):
        if i != 404:
            print(i)
            download(i)
