'''
build
=====

this set of methods is used to compile the lacuher_sync_run.py file into an executable using
pyinstaller

Created on Apr 12, 2019

@author: carlos.anguiano
'''
import os
from shot_grid_sub_2_dailies.build_helper.subprocess_hlp import run_attached
import shutil
import sys


class BuildHelper(object):
    """
    Class that helps automate the complexities of building a .py into an exe

    :param str py_script: base name of the script you're trying to convert
    :param str icon: to the icon to use with the .exe
    :param bool one_file: compile to one file default is True
    :param [str] dependencies: a list of dependencies that need to be copied over to the dist folder make things work
    """

    def __init__(self, py_script, icon=None, one_file=False, dependencies=None, no_console=False):
        self._py_script = py_script
        self._dependacies = dependencies or []
        self._one_file = one_file
        self._no_console = no_console
        self._icon = icon

    @staticmethod
    def _find_pyinstaller():
        paths = [path for path in os.environ['PYTHONPATH'].split(os.pathsep) if path and os.path.isdir(path)]
        for path in paths:
            if os.path.basename(path) != 'site-packages':
                continue
            pytps = os.path.dirname(os.path.dirname(path))
            pyinst_exe = os.path.join(pytps, 'scripts', 'pyinstaller.exe')
            if os.path.isfile(pyinst_exe):
                return pyinst_exe
        return None

    @staticmethod
    def _kill_build_dist_dirs():
        dirs = ('build', 'dist')
        for ddir in dirs:
            if not os.path.isdir(ddir):
                continue

            shutil.rmtree(ddir)

    def _run_build(self, pyinstexe, root):

        # NOTE: never disable console please :D
        args = [pyinstexe]

        if self._one_file:
            args.append('--onefile')

        if self._icon:
            args.extend(['--icon', self._icon])

        for extra in self._dependacies:
            args.extend(['--add-data', extra])

        if self._no_console:
            args.append('--noconsole')

        args.append(self._py_script)
        run_attached(args, cwd=root)

    def build_exe(self):
        """
        build the application with using the parameters pass on on initialization
        """
        pyinst = self._find_pyinstaller()
        if not pyinst:
            raise RuntimeError('could not find pyinstaller.exe')

        # clean out build/dir directories
        root = sys.path[0]
        self._kill_build_dist_dirs()

        # run compiler
        self._run_build(pyinst, root)


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath('.')

    return os.path.join(base_path, relative_path)
