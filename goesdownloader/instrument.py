from noaaclass import noaaclass
import itertools
import sys
import os
from urllib import urlretrieve
import threading
from Queue import Queue
from datetime import datetime
from goescalibration import instrument as calibrator
from netcdf import netcdf as nc


def calculate_destiny(url, destfolder):
    name = calibrator.short(url, 1, None)
    dest = os.path.join(destfolder, name)
    return dest


class DownloadThread(threading.Thread):
    def __init__(self, queue, destfolder):
        super(DownloadThread, self).__init__()
        self.queue = queue
        self.destfolder = destfolder
        self.daemon = True

    def run(self):
        while True:
            url = self.queue.get()
            try:
                self.download_url(url)
            except Exception, e:
                print "   Error: %s"%e
            self.queue.task_done()

    def download_url(self, url):
        # change it to a different format if you require
        dest = calculate_destiny(url, self.destfolder)
        print "[%s] Downloading %s -> %s"%(self.ident, url, dest)
        urlretrieve(url, dest)
        calibrator.calibrate(dest)


class DownloadManager(object):

    def __init__(self, destfolder, numthreads=4):
        self.queue = Queue()
        self.downloaders = map(lambda i: DownloadThread(self.queue, destfolder),
                               range(numthreads))

    def start(self):
        for d in self.downloaders:
            d.start()

    def join(self):
        self.queue.join()

def localsize(localfile):
    with open(localfile, 'rb') as f:
        size = len(f.read())
    return size


def only_incompleted(url, destfolder):
    dest = calculate_destiny(url, destfolder)
    completed = False
    if os.path.isfile(dest):
        try:
            with nc.loader(dest) as root:
                nc.getvar(root, 'data')
                nc.getvar(root, 'lat')
                nc.getvar(root, 'lon')
            completed = True
        except Exception, e:
            print e
    return not completed


def download(username, password, folder, suscription_id=None, name=None,
             datetime_filter=None):
    noaa = noaaclass.connect(username, password)
    manager = DownloadManager(folder)
    suscriptions = noaa.subscribe.gvar_img.get(async=True, hours = 2,
                                               append_files=True)
    compare = (lambda sus: sus['id'] == suscription_id if suscription_id else
               sus['name'] == name)
    suscription = filter(lambda s: compare(s), suscriptions)[0]
    orders = filter(lambda o: o['status'] == 'ready', suscription['orders'])
    files = map(lambda o: o['files']['http'], orders)
    urls = filter(lambda filename: filename[-3:] == '.nc',
                  itertools.chain(*files))
    if datetime_filter:
        get_datetime = lambda f: datetime.strptime(calibrator.short(f),
                                                   "%Y.%j.%H%M%S")
        urls = filter(lambda f: datetime_filter(get_datetime(f)), urls)
    urls = filter(lambda u: only_incompleted(u, folder), urls)
    map(manager.queue.put, urls)
    manager.start()
    manager.join()
    downloaded = map(lambda u: "%s/%s" % (folder, calibrator.short(u, 1, None)),
                     urls)
    return downloaded
