'''
'''
from glob import glob
from logging import getLogger
import os
import re

from pexpect import popen_spawn, EOF


class FFMpegHelper(object):
    '''
    Ffmpeg is a class that contains convince methods that wrap the ffmpeg .exe
    it should help add basic methods to our tools set that will allow us to convert images
    to different formats, convert image sequences to .mov, and dump image sequences out of .movs
    in this library .mov is used generically to refer to a movie container regardless of format (quicktime, mpeg, avi, etc)

    '''

    def __init__(self):

        self.string_padding_regex = re.compile(r'(\d+)$')
        self.log = getLogger('FFMpeg_Hepler')
        self._exe = self._get_exe()

    def extract_padding(self, str_val, as_string=False):
        '''
        extract padding from the input string value

        :param str str_val:
        :param str as_string:
        '''
        match = self.string_padding_regex.search(str_val)

        if not match:
            return None

        if as_string:
            return match.group(1)

        return int(match.group(1))

    def _get_exe(self):
        """
        find ffmpeg exe

        """
        root = os.path.dirname(__file__)
        exepath = os.path.join(root, 'ffmpeg-20191018-feaec3b-win64-static', 'bin', 'ffmpeg.exe')

        if not os.path.isfile(exepath):
            raise RuntimeError('could not find %s' % exepath)

        return exepath

    def _launch_and_track(self, cmd, workdir, qt_pg=None):
        '''
        used to launch ffmpeg and track the progress based on the consoule output
        this is not using stdout as usual, so we use pexpect to track the output

        :param cmd: list of string that make the command flags and values to be launched
        :type cmd: list(str)
        :param workdir: the directory to use the as the current working directory for the process
        :type workdir: str
        :param qt_pg: takes a QProgressbar that will be updated as the process runs
        '''
        thread = popen_spawn.PopenSpawn(cmd, cwd=workdir, encoding='utf-8')
        cpl = thread.compile_pattern_list([EOF, u"frame= *\d+"])

        while True:
            i = thread.expect_list(cpl, timeout=None)

            if i == 0:
                return thread.wait()

            if i != 1 or not qt_pg:
                continue

            val = int(thread.match.group(0).replace('frame=', ''))
            qt_pg.setValue(val)

    def mov_to_mov(self,
                   in_file,
                   output,
                   scale=False,
                   frame_rate=23.98,
                   lut_3d=None,
                   qt_pg=None,
                   codec=None):
        """
        Encode incoming movies to a standard output format

        :param str in_file: the first image that makes up the image sequence
        :param str output: the output for the final movie container
        :param boolean scale: if set to true will scalse down the move to a 720 by 480 square with latter box

        :param float frame_rate: the play back frame rate for the movie (default 23.98)
        :param str lut_3d: path to lut path to be applied to image during encoding
        :param Qt.QtWidgets.QProgressBar qt_pg: optional QProgressBar so that will be kept up to date during the process
        :param codec: Name of codec. Currently support 'mjpeg' and 'h264'.

        :example:

        >>> from btools.utils.image_processing.ffmepg_helper import FFMpegHelper
        >>> input_file = r'C:\myMovie.avi'
        >>> movfile = os.path.join(r'c:\temp\', 'movie.mov') # create movie output
        >>> ffmpg.mov_to_mov(input_file, movfile) #ecode image sequence to .mov
        """
        codec = codec or 'h264'
        out_root = os.path.dirname(output)
        if not os.path.isdir(out_root):
            os.makedirs(out_root)

        cwd = os.path.dirname(in_file)
        cmd = [self._exe, '-y']
        cmd.extend(['-r', str(frame_rate)])
        cmd.extend(['-i', in_file.replace('\\', '/')])

        # set codec
        codec = codec.lower()
        # Motion jpeg, high quality
        if codec == 'mjpeg':
            cmd.extend(['-vcodec', 'mjpeg', '-qscale', '1'])

        # h264 high quality
        elif codec == 'h264':
            cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])

        else:
            raise ValueError("Unsupported codec: %s" % codec)

        vf_cmds = []

        if lut_3d and os.path.isfile(lut_3d):
            vf_cmds.append('lut_3d=file=%s' % os.path.basename(lut_3d))
            cwd = os.path.dirname(lut_3d)

        if scale:
            cmd += ['-aspect', '1.5']
            vf_cmds += ['scale=iw*min(720/iw\,480/ih):ih*min(720/iw\,480/ih)', 'pad=720:480:(720-iw)/2:(480-ih)/2']

        if vf_cmds:
            cmd += ['-vf', ','.join(vf_cmds)]

        cmd.append(output.replace('\\', '/'))

        return self._launch_and_track(cmd, cwd, qt_pg=qt_pg)

    def gen_image_sequence_data_from_file(self, input_image):
        root, base = os.path.split(input_image)
        fname, ext = os.path.splitext(base)

        padding = self.extract_padding(fname, as_string=True)
        if not padding:
            raise ValueError('%s is not part of an input_image sequence (no padding)' % input_image)
        subname = fname[:-len(padding)]
        search = os.path.join(root, subname + '*' + ext)

        images = glob(search)
        pre_regex = os.path.join(root, subname).lower()
        pre_regex = pre_regex.replace('\\', '\\\\')
        confirm_regex = r'(%s)(\d+)(%s)$' % (pre_regex, ext.lower())
        cregex = re.compile(confirm_regex, flags=re.IGNORECASE)

        images = [img for img in images if cregex.match(img)]
        images.sort(key=lambda x: x.lower())

        if not images:
            raise ValueError('Could not determine input_image list from path %s' % input_image)

        return self.extract_padding(images[0][:-len(ext)], as_string=True), len(images), images[0], ext

    def image_list_to_mov(self,
                          input_image,
                          output,
                          scale=False,
                          frame_rate=23.98,
                          lut_3d=None,
                          qt_pg=None,
                          codec=None):
        '''
        this method is for encodeing image sequences into movies

        :param str first_img: the first image that makes up the image sequence
        :param str output: the output for the final movie container
        :param boolean scale: if set to true will scalse down the move to a 720 by 480 square with latter box

        :param float frame_rate: the play back frame rate for the movie (default 23.98)
        :param str lut_3d: path to lut path to be applied to image during encoding
        :param Qt.QtWidgets.QProgressBar qt_pg: optional QProgressBar so that will be kept up to date during the process
        :param codec: Name of codec. Currently support 'mjpeg' and 'h264'.

        :example:

        >>> from btools.utils.image_processing.ffmepg_helper import FFMpegHelper
        >>> import os
        >>> from glob import glob
        >>> ffmpg = FFMpegHelper()
        >>> image_seq = glob(r'c:\image_sequence_folder\*.jpg') # collect a sequence of jpegs
        >>> movfile = os.path.join(r'c:\temp\', 'movie.mov') # create movie output
        >>> ffmpg.image_list_to_mov(image_seq[0], movfile) #ecode image sequence to .mov

        '''
        codec = codec or 'h264'

        start_frame, img_count, first_img, ext = self.gen_image_sequence_data_from_file(input_image)

        # NOTE: set progress bar to match number of frames
        if qt_pg:
            qt_pg.setValue(0)
            qt_pg.setMaximum(img_count)

        img_root, base_name = os.path.split(first_img)

        input_img = os.path.join(img_root, base_name.replace(start_frame + ext, '%04d' + ext))

        out_root = os.path.dirname(output)

        if not os.path.isdir(out_root):
            os.makedirs(out_root)

        cwd = os.path.dirname(input_img)
        cmd = [self._exe, '-y']

        cmd.extend(['-start_number', str(int(start_frame))])
        cmd.extend(['-f', 'image2'])
        cmd.extend(['-r', str(frame_rate)])
        cmd.extend(['-i', input_img.replace('\\', '/')])

        # set codec
        codec = codec.lower()
        # Motion jpeg, high quality
        if codec == 'mjpeg':
            cmd.extend(['-vcodec', 'mjpeg', '-qscale', '1'])

        # h264 high quality
        elif codec == 'h264':
            cmd.extend(['-c:v', 'libx264', '-preset', 'slow', '-crf', '18'])

        else:
            raise ValueError("Unsupported codec: %s" % codec)

        vf_cmds = []

        if lut_3d and os.path.isfile(lut_3d):
            vf_cmds.append('lut_3d=file=%s' % os.path.basename(lut_3d))
            cwd = os.path.dirname(lut_3d)

        if scale:
            cmd += ['-aspect', '1.5']
            vf_cmds += [r'scale=iw*min(720/iw\,480/ih):ih*min(720/iw\,480/ih)', r'pad=720:480:(720-iw)/2:(480-ih)/2']

        if vf_cmds:
            cmd += ['-vf', ','.join(vf_cmds)]

        cmd.append(output.replace('\\', '/'))
        return self._launch_and_track(cmd, cwd, qt_pg=qt_pg)


if __name__ == '__main__':
    FFMPEG = FFMpegHelper()
    print(FFMPEG._get_exe())
