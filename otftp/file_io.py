import logging
import os
import os.path as opath
from .netascii import Netascii


def sanitize_fname(fname):
    """
    Ensures that fname is a path under the current working directory.
    """
    return fname.decode('ASCII')
    # root_dir = os.getcwd()
    # return opath.join(
    #     bytes(root_dir, encoding='ascii'),
    #     opath.normpath(
    #         b'/' + fname).lstrip(b'/'))


class FileReader(object):
    """
    A wrapper around a regular file that implements:
    - read_chunk - for closing the file when bytes read is
      less than chunk_size.
    - finished - for easier notifications
    interfaces.
    When it goes out of scope, it ensures the file is closed.
    """

    def __init__(self, fname, chunk_size=0, mode=None):
        self.fname = sanitize_fname(fname)
        self.chunk_size = chunk_size
        self._f = None
        self._f = self._open_file()
        self.finished = False

        if mode == b'netascii':
            self._f = Netascii(self._f)

    def _open_file(self):
        return open(self.fname, 'rb')

    def file_size(self):
        return os.stat(self.fname).st_size

    def read_chunk(self, size=None):
        size = size or self.chunk_size
        if self.finished:
            return b''

        data = self._f.read(size)

        if not data or (size > 0 and len(data) < size):
            self._f.close()
            self.finished = True

        return data

    def __del__(self):
        if self._f and not self._f.closed:
            self._f.close()


class OberonFileReader(FileReader):
    """
    A file reader which looks for files in the Oberon file hierarchy
    """

    OBERON_LIBS_DIR = 'Oberon/Lib'
    TOP_DIR = 'Oberon'

    def __init__(self, files_dir, *args, **kwargs):
        self.log = logging.getLogger('OberonFileReader')
        self.log.setLevel(logging.INFO)
        self._files_dir = files_dir
        # we check if the files directory is under 'Oberon'
        self._is_under_oberon_dir = self.TOP_DIR in self._files_dir.split(os.sep)
        super().__init__(*args, **kwargs)
        self._current_dir = self._files_dir

    def _open_file(self):
        """Looks for file and opens it"""
        self._current_dir = self._files_dir
        if self._is_under_oberon_dir:
            return self._open_file_under_oberon_dir()
        else:
            res =  open(self._current_file_path(), 'rb')
            self.log.info('Transferring {}'.format(self._current_file_path()))
            return res

    def _open_file_under_oberon_dir(self):
        # looking in files_dir then in all parent dirs until Oberon
        while not self._is_top_dir():
            self.log.debug('looking for {} in {}'.format(self.fname, self._current_dir))
            if self._file_exists_in_current_dir():
                self.log.info('Transferring {}'.format(self._current_file_path()))
                return open(self._current_file_path(), 'rb')
            else:
                self._go_to_parent_dir()

        # looking in special directories
        self._current_dir = os.path.join(self._files_dir, self.OBERON_LIBS_DIR)
        if self._file_exists_in_current_dir():
            self.log.debug('looking for {} in {}'.format(self.fname, self._current_dir))
            return open(self._current_file_path())
        else:
            self.log.debug('{} not found'.format(self._current_file_path()))
            # file not found, we try to open it, which will raise a file not found error
            open(os.path.join(self._files_dir, self.fname), 'rb')

    def _go_to_parent_dir(self):
        """ Goes up a directory """
        self._current_dir = os.path.abspath(os.path.dirname(self._current_dir))

    def _is_top_dir(self):
        """ Returns True if we are in the top directory """
        return os.path.basename(self._current_dir) == self.TOP_DIR

    def _current_file_path(self):
        return os.path.join(self._current_dir, self.fname)

    def _file_exists_in_current_dir(self):
        return os.path.isfile(self._current_file_path())


class FileWriter(object):
    """
    Wrapper around a regular file that implements:
    - write_chunk - for closing the file when bytes written
      is less than chunk_size.
    When it goes out of scope, it ensures the file is closed.
    """
    def __init__(self, fname, chunk_size, mode=None):
        self.fname = sanitize_fname(fname)
        self.chunk_size = chunk_size
        self._f = None
        self._f = self._open_file()

        if mode == b'netascii':
            self._f = Netascii(self._f)

    def _open_file(self):
        return open(self.fname, 'xb')

    def _flush(self):
        if self._f:
            self._f.flush()

    def write_chunk(self, data):
        bytes_written = self._f.write(data)

        if not data or len(data) < self.chunk_size:
            self._f.close()

        return bytes_written

    def __del__(self):
        if self._f and not self._f.closed:
            self._f.close()
