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
import logging
import logging.handlers


logger = logging.getLogger('goesdownloader')
logger.setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    "goesdownloader.out", maxBytes=20, backupCount=5)
logger.addHandler(handler)



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
                logger.error("   Error: %s" % e)
            self.queue.task_done()

    def download_url(self, url):
        # change it to a different format if you require
        ftp, http = url
        dest = calculate_destiny(http, self.destfolder)
        msg = "[%s] %s %s -> %s"
        logger.info(msg % ("Downloading", self.ident, ftp, dest))
        try:
            # Try ftp...
            urlretrieve(ftp, dest)
        except Exception:
            logger.info(msg % ("Alternative downloading", self.ident,
                                ftp, dest))
            # Try http...
            urlretrieve(http, dest)
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
    if os.path.exists(dest):
        try:
            with nc.loader(dest) as root:
                nc.getvar(root, 'data')
                nc.getvar(root, 'lat')
                nc.getvar(root, 'lon')
            completed = True
        except (OSError, IOError, Exception):
            logger.error("The file %s was broken." % dest)
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
    http_files = map(lambda o: o['files']['http'], orders)
    ftp_files = map(lambda o: o['files']['ftp'], orders)
    files = zip(itertools.chain(*ftp_files), itertools.chain(*http_files))
    urls = filter(lambda filename: filename[0][-3:] == '.nc',
                  files)
    if datetime_filter:
        get_datetime = lambda f: datetime.strptime(calibrator.short(f),
                                                   "%Y.%j.%H%M%S")
        urls = filter(lambda f: datetime_filter(get_datetime(f[0])), urls)
    urls = filter(lambda u: only_incompleted(u[0], folder), urls)
    map(manager.queue.put, urls)
    manager.start()
    manager.join()
    downloaded = map(lambda u: "%s/%s" % (folder, calibrator.short(u[1], 1, None)),
                     urls)
    return downloaded
