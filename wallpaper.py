import sys
import wget
import os
import requests
import random
import threading
from threading import Thread
import time
from filelock import Timeout, FileLock

root = os.path.expanduser('~/Pictures/Wallpapers')

image_names = []
names_lock = threading.Lock()
interval = 10.0
refresh = 0.5

def download(filename, url):
    if not os.path.exists(os.path.join(root, filename)):
        print(f'{threading.current_thread().name} downloading {filename}')
        wget.download(url, os.path.join(root, filename))
    with names_lock:
        image_names.append(filename)
    print(f'{threading.current_thread().name} Downloaded {filename}')

def wallpaper_list():
    last = ""
    while True:
        starttime = time.monotonic()
        names_lock.acquire()
        if len(image_names) > 0:
            name = random.choice(image_names)
            names_lock.release()
            if name == last:
                continue
            last = name
            yield os.path.join(root, name)
            print(f'{threading.current_thread().name} Changing wallpaper to {name}')
            time.sleep(max(0, interval - (time.monotonic() - starttime))) 
                       
        else:
            names_lock.release()
            print(f'{threading.current_thread().name} Waiting for images')
            time.sleep(max(0, refresh - (time.monotonic() - starttime)))

def main():
    # Download the image from 'url' and save it locally under 'file_name':
    url = "https://www.bing.com/HPImageArchive.aspx"

    result = requests.get(url,{
        'format': 'js',
        'idx': 0,
        'n': 5,
        'mkt': 'en-US',
        'uhd': 1,
        'uhdwidth': 2560,
        'uhdheight': 1080
    }).json().get('images')

    for image in result:
        file_name = image.get('startdate') + '.jpg'
        url = 'https://www.bing.com' + image.get('url')
        Thread(target=download, args=(file_name, url)).start()

    print(f'{threading.current_thread().name} Starting Wallpaper Changer')

    for wallpaper in wallpaper_list():
        os.system(f'feh --bg-fill {wallpaper}')


if __name__ == '__main__':
    lock = FileLock(root + '.lock', timeout=0)
    try:
        lock.acquire()
    except Timeout:
        print('Wallpaper already running')
        sys.exit(1)
    sys.exit(main())