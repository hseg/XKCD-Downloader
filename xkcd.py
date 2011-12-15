# XKCD Downloader
# Downloads an XKCD comic given the comic number.
# Filters the data and reformats it.

# TODO: Generate Markdown instead of HTML, more generic
# TODO: Refactor
# TODO: Command line arguments

XKCD_IP='72.26.203.99'

from urllib.request import urlopen as uopen
import string
import urllib.request
import json
import sys
import os

def download(num):
# Generate JSON URL
    url = 'http://' + XKCD_IP + '/{0}/info.0.json'.format(num)

# Download JSON
    while True:
        try:
            comic = uopen(url).readall().decode()
            break
        except:
            raise

    # Open JSON file
    data = json.loads(comic)

    # Save JSON
    json_file = open('{0}.json'.format(num), 'w', encoding='utf-8')
    json_file.write(str(data))

    # Create HTML from template
    data['date'] = '{0}/{1}/{2}'.format(data['day'], data['month'], data['year'])
    data['url'] = url.rsplit('/', 1)[0] + '/'
    meta_entries = ['num', 'date', 'news', 'link']
    meta_labels = {'num': 'Number:', 'date': 'Published:', 'news': 'News:',
                'link': 'Link:'}
    head = string.Template('''
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
    entry = string.Template('<tr><td><b>${label}</b></td><td>${value}</td></tr>')
    tail = string.Template('''
</table>
<a href="${img}"><img src="${num}.png" title=${alt} /></a>
<p>${alt}</p>
<br/><br/>
<p>${transcript}
</body>
</html>''')

    # Write HTML and image to file
    file = open('{0}.html'.format(num), 'w', encoding='utf-8')
    file.write(head.substitute(data))
    for i in meta_entries:
        if data[i]:
            file.write(entry.substitute({'label': meta_labels[i], 'value': data[i]}))
    file.write(tail.substitute(data))

    image = uopen(data['img'])
    img = open('{0}.png'.format(num), 'bw')
    img.write(image.read())

if __name__ == "__main__":
    # Get latest comic
    url = 'http://' + XKCD_IP + '/info.0.json'

    # Download JSON
    try:
        comic = uopen(url).readall().decode()
    except:
        raise e

    # Get comic number
    num = json.loads(comic)['num']

    os.chdir('..\XKCD')
    for i in range(1, num+1):
        if i != 404:
            print(i)
            download(i)
