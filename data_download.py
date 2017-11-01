from __future__ import print_function
import requests
import os
import posixpath

url_template = r'http://cdn.gea.esac.esa.int/Gaia/tgas_source/csv/TgasSource_000-000-{index:03d}.csv.gz'


def main():
    loader = True

    for index in xrange(16):
        url = url_template.format(index=index)
        filename = posixpath.basename(url)

        if os.path.isfile(filename):
            print('Skipped', filename)
            continue

        print('Downloading', filename)

        response = requests.get(url, stream=True)

        with open(filename, 'wb') as fp:
            for chunk in response.iter_content(1024):
                size = os.path.getsize(filename)/1024**2
                fp.write(chunk)
                if loader is True:
                    print('| {:d} MB downloaded'.format(size), end='\r')
                else:
                    print('_ {:d} MB downloaded'.format(size), end='\r')
                loader = not loader

if __name__ == '__main__':
    main()
