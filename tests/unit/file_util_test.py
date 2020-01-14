import os
import unittest as t
from unittest import mock
from contextlib import contextmanager
from io import BytesIO

from otftp.file_io import FileReader, FileWriter, sanitize_fname


class FileReaderTest(t.TestCase):
    def setUp(self):
        self.mock_file = BytesIO()
        self.filename = b'LICENSE'
        self._file_content = b'''\
The MIT License (MIT)

Copyright for portions of project otftp are held by sirMackk, 2016] as part of project py3tftp.
All other copyright for project otftp are held by [Andrea Peter, 2019].

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
        with self.mock_file_open():
            self.reader = FileReader(self.filename)

    class FileMock(BytesIO):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._closed = False

        def close(self):
            super().close()
            self._closed = True

    @contextmanager
    def mock_file_open(self):
        with mock.patch('builtins.open',
                        mock.MagicMock(return_value=self.FileMock(self._file_content))):
            yield

    @contextmanager
    def mock_file_not_found_open(self):
        with mock.patch('builtins.open',
                        mock.MagicMock(side_effect=FileNotFoundError)):
            yield

    def test_reads_file(self):
        with self.mock_file_open():
            chunk = self.reader.read_chunk(2048)

            with open(self.filename, 'rb') as f:
                self.assertEqual(f.read(), chunk)

    def test_reads_n_bytes(self):
        bytes_to_read = 12
        chunk = self.reader.read_chunk(bytes_to_read)

        with self.mock_file_open():
            with open(self.filename, 'rb') as f:
                self.assertEqual(f.read(bytes_to_read), chunk)

    def test_still_has_data_to_read(self):
        bytes_to_read = 4
        data = BytesIO()
        while not self.reader.finished:
            data.write(self.reader.read_chunk(bytes_to_read))

        with self.mock_file_open():
            with open(self.filename, 'rb') as f:
                self.assertEqual(f.read(), data.getvalue())

        self.assertTrue(self.reader.finished)

    def test_raises_doesnt_exist_exc(self):
        with self.mock_file_not_found_open():
            with self.assertRaises(FileNotFoundError):
                reader = FileReader(b'DOESNT_EXIST')
                reader.read_chunk()

    def test_file_closed_after_complete_reading(self):
        self.reader.read_chunk(len(self._file_content) + 1)
        self.assertTrue(self.reader._f.closed)


class FileWriterTest(t.TestCase):
    def setUp(self):
        self.filename = b'TEST_FILE'
        self.msg = b'test msg'
        self.chk_size = len(self.msg)
        self.writer = FileWriter(self.filename, self.chk_size)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.unlink(self.filename)

    def test_writes_full_file_to_disk(self):
        self.writer.write_chunk(self.msg)

        self.assertTrue(os.path.exists(self.filename))

        self.writer._flush()
        with open(self.filename, 'rb') as f:
            self.assertEqual(self.msg, f.read())

    def test_write_chunk_returns_no_bytes_written(self):
        bytes_written = self.writer.write_chunk(self.msg)
        self.assertEqual(len(self.msg), bytes_written)

    def test_doesnt_overwrite_file_raises_exc(self):
        self.writer.write_chunk(self.msg)
        with self.assertRaises(FileExistsError):
            writer2 = FileWriter(self.filename, len(self.msg))
            writer2.write_chunk(self.msg)

    def test_fd_closed_after_everything_written_out(self):
        self.writer.write_chunk(self.msg)

        fd = self.writer._f.fileno()
        self.writer._flush()

        # simulate the writer obj going out of scope
        del self.writer

        with self.assertRaises(OSError):
            os.fstat(fd)


class TestSanitizeFname(t.TestCase):
    @classmethod
    def setUpClass(cls):
        from os import getcwd
        from os.path import join as path_join
        cls.target_dir = bytes(
            path_join(getcwd(), 'tmp/testfile'),
            encoding='ascii')

    def test_under_root_dir(self):
        fname = b'/tmp/testfile'
        self.assertEqual(sanitize_fname(fname), self.target_dir)

    def test_dir_traversal(self):
        fname = b'../../../../../../tmp/testfile'
        self.assertEqual(sanitize_fname(fname), self.target_dir)
