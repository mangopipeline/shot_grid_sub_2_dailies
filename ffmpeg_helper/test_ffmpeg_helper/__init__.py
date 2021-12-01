from glob import glob
import os
from shot_grid_sub_2_dailies.ffmpeg_helper import FFMpegHelper
from tempfile import gettempdir
import unittest


class FFMpegHelperTest(unittest.TestCase):
    def setUp(self):
        self._ffmpeg = FFMpegHelper()
        self._mov_output = os.path.join(gettempdir(), 'ffmepg_test_render.mov')
        if os.path.isfile(self._mov_output):
            os.unlink(self._mov_output)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        if os.path.isfile(self._mov_output):
            os.unlink(self._mov_output)

    def test_image_list_to_mov(self):
        self.assertFalse(os.path.isfile(self._mov_output))

        sfiles = os.path.join(os.path.dirname(__file__),
                              'test_files',
                              'image_seq',
                              'box*.jpg')

        files = glob(sfiles)
        self._ffmpeg.image_list_to_mov(files[0],
                                       self._mov_output)

        self.assertTrue(os.path.isfile(self._mov_output))


if __name__ == '__main__':
    unittest.main()
