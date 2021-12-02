
"""

conviance library for handling launching track and untrack subprocess from python

Created on Feb 26, 2019

@author: carlos.anguiano
"""

from subprocess import Popen, PIPE


def _simple_logging(msg):
    print(msg)


def run_attached(args, env=None, cwd=None, log=None):
    """

    :param list args:
    :param dict env:
    :param str cwd:
    :param object log:
    """
    log = log or _simple_logging
    kill_file = None

    log('running %s' % ' '.join(args))

    kwargs = {'cwd': cwd,
              'env': env,
              'stdout': PIPE}

    # TODO: remove this wrapper when we move away from 2.7 and use subprocess.Popen directly
    with Popen(args, **kwargs) as process:
        fail_errors = []
        happy_exit = False

        while process.poll() is None:
            # resume none kill file based routine
            msg = process.stdout.readline().strip()

            if not msg:
                continue

            log(msg.decode('utf-8'))

    if kill_file and not happy_exit:
        raise RuntimeError('the process either crash or was ended by the user')

    if kill_file and fail_errors:
        errs_msg = '\n'.join(fail_errors)
        raise RuntimeError(errs_msg)

    if process.returncode:
        raise RuntimeError('%s did not exit properly' % args[0])
