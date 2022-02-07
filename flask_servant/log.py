import os
import sys
import logging
import contextlib
import logging
import datetime
import traceback as tb
from io import StringIO
import sys

thisDir = os.path.abspath(os.path.dirname(__file__))
logDir = os.path.join(os.path.dirname(thisDir), 'Logs')

default_format = '%(asctime)s - %(levelname)s - %(message)s'
date_format='%Y-%m-%d %H:%M:%S'

def timestamp(prefix='', suffix=''):
    return ''.join([prefix, datetime.datetime.now().isoformat().split('.')[0].replace(':', '-'), suffix])


def log(msg, level='info'):
    """prints message to stdout and also to log file.

    Args:
        *args: the message arguments
        level (str, optional): [description]. Defaults to 'info'.
    """
    logger = logging.getLogger()
    getattr(logger, level)(msg)
    print(msg)
        
def set_logger_context(prefix: str=None, format: str=default_format, datefmt :str=date_format, level=logging.DEBUG, **kwargs):
    """sets up the basic configuration for the logger

    Args:
        prefix (str, optional): [description]. Defaults to 'Ticketing_'.
        format ([type], optional): [description]. Defaults to default_format.
        datefmt ([type], optional): [description]. Defaults to date_format.
        level ([type], optional): [description]. Defaults to logging.DEBUG.
    """
    log_file = None
    if prefix:
        log_file = os.path.join(logDir, timestamp(prefix, suffix='.log'))
        try:
            if not os.path.exists(logDir):
                os.makedirs(logDir)
        except:
            pass
    logging.basicConfig(filename=log_file, format=format, datefmt=date_format, level=level, **kwargs)


@contextlib.contextmanager
def log_context(prefix: str=None, format=default_format, datefmt=date_format, level=logging.INFO, **kwargs):
    set_logger_context(prefix, format, datefmt, level, **kwargs)
    try:
        yield
    except Exception:
        # We want the _full_ traceback with the context
        # First we get the current call stack, which constitutes the "top",
        # it has the context up to the point where the context manager is used
        top_stack = StringIO()
        tb.print_stack(file=top_stack)
        top_lines = top_stack.getvalue().strip('\n').split('\n')
        top_stack.close()
        # Get "bottom" stack from the local error that happened
        # inside of the "with" block this wraps
        exc_type, exc_value, exc_traceback = sys.exc_info()
        bottom_stack = StringIO()
        tb.print_tb(exc_traceback, file=bottom_stack)
        bottom_lines = bottom_stack.getvalue().strip('\n').split('\n')
        # Glue together top and bottom where overlap is found
        bottom_cutoff = 0
        for i, line in enumerate(bottom_lines):
            if line in top_lines:
                # start of overlapping section, take overlap from bottom
                top_lines = top_lines[:top_lines.index(line)]
                bottom_cutoff = i
                break
        bottom_lines = bottom_lines[bottom_cutoff:]
        tb_lines = top_lines + bottom_lines

        tb_string = '\n'.join(
            ['Traceback (most recent call last):'] +
            tb_lines +
            ['{}: {}'.format(exc_type.__name__, str(exc_value))]
        )
        bottom_stack.close()
        # Log the combined stack
        log('Full Error Traceback:\n{}'.format(tb_string), level="error")


def timeit(function):
    def wrapper(*args, **kwargs):
        st = datetime.datetime.now()
        output = function(*args, **kwargs)
        elapsed = str(datetime.datetime.now() - st)
        if hasattr(function, 'im_class'):
            fname = '.'.join([function.im_class.__name__, function.__name__])
        else:
            fname = function.__name__
        log(f'function {fname} from {sys.modules[function.__module__]} completed - elapsed time: {elapsed}')
        return output
    return wrapper
