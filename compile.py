'''
Created on Dec 1, 2021

@author: carlos.anguiano
'''
'''
Created on Sep 2, 2021

@author: carlos.anguiano
========================

this script allows us to compile the bsu python client into an executable
'''
from glob import iglob
import os
from shot_grid_sub_2_dailies.build_helper import BuildHelper


_ROOTDIR = os.path.dirname(__file__)


def _collect_files_in_dir(dir_path):
    out = []
    diritems = iglob(os.path.join(dir_path, '*'))

    while diritems:
        ndirs = []
        for item in diritems:
            if os.path.isfile(item):
                out.append(item)
                continue

            ndirs.extend(iglob(os.path.join(item, '*')))

        diritems = ndirs

    return out


if __name__ == '__main__':

    _EXTRA_DATA = []

    #_EXTRA_DATA.append(r"%s;data" % os.path.join(_PYTOOLS_DIR, r'btools\apis\config\config.yml'))

    extra_dirs = [r'ffmpeg_helper\ffmpeg-20191018-feaec3b-win64-static',
                  'views']

    for mdir in extra_dirs:
        fullpath = os.path.join(_ROOTDIR, mdir)
        exfiles = _collect_files_in_dir(fullpath)
        for exfile in exfiles:
            relative = exfile[len(_ROOTDIR) + 1:]
            if not relative.startswith('views'):
                _EXTRA_DATA.append(r'%s;shot_grid_sub_2_dailies\%s' % (relative, os.path.dirname(relative)))
            else:
                _EXTRA_DATA.append(r'%s;%s' % (relative, os.path.dirname(relative)))

    # NOTE: let's build our app

    _BUILDER = BuildHelper('sub2d.py',

                           one_file=True,
                           no_console=True,
                           dependencies=_EXTRA_DATA)

    _BUILDER.build_exe()
