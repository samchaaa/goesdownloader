import unittest
from goesdownloader import instrument as goes
from goescalibration import instrument as calibrator
import os
import glob
from datetime import datetime, timedelta
from netcdf import netcdf as nc


class assert_downloaded(object):

    def __init__(self, test_case, should_download):
        self.files = []
        self.should_download = should_download
        self.assertEquals = test_case.assertEquals
        self.assertNotEquals = test_case.assertNotEquals
        self.assertAlmostEqual = test_case.assertAlmostEqual
        self.assertLessEqual = test_case.assertLessEqual
        self.directory = test_case.directory

    def __enter__(self):
        self.initial_files = glob.glob('%s/*.nc' % self.directory)
        return self

    def downloaded(self, file_list):
        self.files = file_list
        self.initial_files = filter(lambda f: f not in self.files,
                                    self.initial_files)

    def __exit__(self, type, value, traceback):
        self.initial_size = len(self.initial_files)
        final_size = len(glob.glob('%s/*.nc' % self.directory))
        files = self.files
        if files:
            # Test if it downloaded something.
            self.assertNotEquals(final_size, self.initial_size)
            the_size = final_size - self.initial_size
            self.assertEquals(len(files), the_size)
            # Test if it calibrated the downloaded files.
            with nc.loader(files) as root:
                counts = nc.getvar(root, 'counts_shift')
                self.assertEquals(counts.shape, (the_size, 1, 1))
                self.assertEquals(counts[0], 32.)
                space = nc.getvar(root, 'space_measurement')
                self.assertEquals(space.shape, (the_size, 1, 1))
                self.assertEquals(space[0], 29.)
                prelaunch_0 = nc.getvar(root, 'prelaunch_0')
                self.assertEquals(prelaunch_0.shape, (the_size, 1, 1))
                self.assertAlmostEqual(prelaunch_0[0], 0.61180001, 6)
                prelaunch_1 = nc.getvar(root, 'prelaunch_1')
                self.assertEquals(prelaunch_1.shape, (the_size, 1, 1))
                self.assertAlmostEqual(prelaunch_1[0], 0.00116, 6)
                postlaunch = nc.getvar(root, 'postlaunch')
                self.assertEquals(postlaunch.shape, (the_size, 1, 1))


class TestInstrument(unittest.TestCase):

    def setUp(self):
        self.directory = 'data'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def assert_downloaded_files(self, should_download=None):
        return assert_downloaded(self, should_download)

    def test_download(self):
        with self.assert_downloaded_files() as validation:
            files = goes.download('noaa.gvarim', 'noaaadmin', self.directory,
                              suscription_id='55253')
            validation.downloaded(files)

    def test_download_with_datetime_filter(self):
        should_download = lambda dt: dt.hour - 4 >= 5 and dt.hour - 4 <= 20
        with self.assert_downloaded_files(should_download) as validation:
            files = goes.download('noaa.gvarim', 'noaaadmin', self.directory,
                                  name='goesdownloader test',
                                  datetime_filter=should_download)
            validation.downloaded(files)


if __name__ == '__main__':
        unittest.main()
