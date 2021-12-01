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

    def test_gen_image_sequence_data_from_file(self):
        image = os.path.join(os.path.dirname(__file__), r'test_files\image_seq\box0004.jpg')
        fimage = os.path.join(os.path.dirname(__file__), r'test_files\image_seq\box0000.jpg')
        self.assertTrue(os.path.isfile(image))
        targetvalue = ('0000', 11, fimage, '.jpg')
        testvalue = self._ffmpeg.gen_image_sequence_data_from_file(image)

        self.assertTupleEqual(targetvalue, testvalue)


if __name__ == '__main__':
    unittest.main()
