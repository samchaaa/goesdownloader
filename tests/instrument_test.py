import unittest
from goesdownloader import instrument as goes
from goescalibration import instrument as calibrator
import os
import glob
from datetime import datetime, timedelta
from netcdf import netcdf as nc


class TestInstrument(unittest.TestCase):

    def setUp(self):
        self.directory = 'data'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

    def test_download_with_datetime_filter(self):
        should_download = lambda dt: dt.hour - 4 >= 5 and dt.hour - 4 <= 20
        initial_files = glob.glob('%s/*.nc' % self.directory)
        initial_size = len(initial_files)
        files = goes.download('noaa.gvarim', 'noaaadmin', self.directory,
                              name='goesdownloader test',
                              datetime_filter=should_download)
        final_size = len(glob.glob('%s/*.nc' % self.directory))
        if files:
            # Test if it downloaded something.
            self.assertNotEquals(final_size, initial_size)
            self.assertEquals(len(files), final_size - initial_size)
            # Test if it calibrated the downloaded files.
            with nc.loader(files) as root:
                counts = nc.getvar(root, 'counts_shift')
                self.assertEquals(counts.shape, (final_size, 1, 1))
                self.assertEquals(counts[0], 32.)
                space = nc.getvar(root, 'space_measurement')
                self.assertEquals(space.shape, (final_size, 1, 1))
                self.assertEquals(space[0], 29.)
                prelaunch_0 = nc.getvar(root, 'prelaunch_0')
                self.assertEquals(prelaunch_0.shape, (final_size, 1, 1))
                self.assertAlmostEqual(prelaunch_0[0], 0.61180001, 6)
                prelaunch_1 = nc.getvar(root, 'prelaunch_1')
                self.assertEquals(prelaunch_1.shape, (final_size, 1, 1))
                self.assertAlmostEqual(prelaunch_1[0], 0.00116, 6)
                postlaunch = nc.getvar(root, 'postlaunch')
                self.assertEquals(postlaunch.shape, (final_size, 1, 1))
        else:
            last_image = (calibrator.get_datetime(initial_files[-1])
                          if initial_files else datetime.utcnow())
            next_image = last_image + timedelta(minutes=30)
            if should_download(next_image):
                time_from_last_image = datetime.utcnow() - last_image
                self.assertLessEqual(time_from_last_image,
                                     timedelta(minutes=30))


if __name__ == '__main__':
        unittest.main()
