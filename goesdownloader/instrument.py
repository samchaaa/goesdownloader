from noaaclass import noaaclass
import itertools
import sys
import os
import urllib
import threading
from Queue import Queue
from datetime import datetime
from goescalibration import instrument as calibrator


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
            except Exception,e:
                print "   Error: %s"%e
            self.queue.task_done()

    def download_url(self, url):
        # change it to a different way if you require
        name = calibrator.short(url, 1, None)
        dest = os.path.join(self.destfolder, name)
        print "[%s] Downloading %s -> %s"%(self.ident, url, dest)
        urllib.urlretrieve(url, dest)
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
    map(manager.queue.put, urls)
    manager.start()
    manager.join()
    downloaded = map(lambda u: "%s/%s" % (folder, calibrator.short(u, 1, None)),
                     urls)
    return downloaded