# -*- coding: utf-8 -*-

"""
Testing OberonFileReader
"""

from contextlib import contextmanager
from unittest import mock, TestCase

from file_io import OberonFileReader


class OberonFileReaderTest(TestCase):
    pass

    def setUp(self) -> None:
        self.path = 'some/path'
        self.path_desc = 'path description'
        self.expected_msg = f'{self.path_desc}: "{self.path}" '

    @contextmanager
    def mock_file(self, exists: bool, is_file: bool, has_permission: bool):
        with mock.patch('os.path.exists', mock.MagicMock(return_value=exists)):
            with mock.patch('os.path.isfile', mock.MagicMock(return_value=is_file)):
                with mock.patch('os.access', mock.MagicMock(return_value=has_permission)):
                    yield

    @contextmanager
    def mock_folder(self,
                    exists: bool = True,
                    is_dir: bool = True,
                    has_permission: bool = True):
        with mock.patch('os.path.exists', mock.MagicMock(return_value=exists)):
            with mock.patch('os.path.isdir', mock.MagicMock(return_value=is_dir)):
                with mock.patch('os.access', mock.MagicMock(return_value=has_permission)):
                    yield

    def test(self):
        self.fail("Test this!")

    # def test_can_read_file_ok(self):
    #     with self.mock_file(True, True, True):
    #         self.file_checker.check_can_read_file('path_desc', 'some/path')
    #
    # def test_can_read_file_does_not_exist(self):
    #     with self.mock_file(exists=False, is_file=True, has_permission=True):
    #         with self.assertRaises(DoesNotExist) as ctx:
    #             self.file_checker.check_can_read_file('path_desc', 'some/path')
    #         expected_msg = 'path_desc: "some/path" does not exist'
    #         self.assertEqual(expected_msg, str(ctx.exception))
    #
    # def test_can_read_file_not_a_file(self):
    #     with self.mock_file(exists=True, is_file=False, has_permission=True):
    #         with self.assertRaises(NotAFile) as ctx:
    #             self.file_checker.check_can_read_file('path_desc', 'some/path')
    #         expected_msg = 'path_desc: "some/path" is not a file'
    #         self.assertEqual(expected_msg, str(ctx.exception))
    #
    # def test_can_read_file_no_permission(self):
    #     with self.mock_file(exists=True, is_file=True, has_permission=False):
    #         with self.assertRaises(NoReadPermission) as ctx:
    #             self.file_checker.check_can_read_file('path_desc', 'some/path')
    #         expected_msg = 'path_desc: "some/path" no read permission'
    #         self.assertEqual(expected_msg, str(ctx.exception))
    #
    # def test_can_write_folder_ok(self):
    #     with self.mock_folder(True, True, True, True):
    #         self.file_checker.check_can_write_folder('path_desc', 'some/path')
    #
    # def test_can_write_folder_does_not_exist(self):
    #     with self.mock_folder(exists=False):
    #         with self.assertRaises(DoesNotExist) as ctx:
    #             self.file_checker.check_can_write_folder(self.path_desc, self.path)
    #         self.assertEqual(self.expected_msg + 'does not exist', str(ctx.exception))
    #
    # def test_can_write_folder_not_a_folder(self):
    #     with self.mock_folder(is_dir=False):
    #         with self.assertRaises(NotAFolder) as ctx:
    #             self.file_checker.check_can_write_folder(self.path_desc, self.path)
    #         self.assertEqual(self.expected_msg + 'is not a folder', str(ctx.exception))
    #
    # def test_can_write_folder_no_permission(self):
    #     with self.mock_folder(has_permission=False):
    #         with self.assertRaises(NoWritePermission) as ctx:
    #             self.file_checker.check_can_write_folder(self.path_desc, self.path)
    #         self.assertEqual(self.expected_msg + 'no write permission', str(ctx.exception))
    #
    # def test_can_write_folder_cannot_create_tmp_file(self):
    #     with self.mock_folder(can_create_tmp_file=False):
    #         with self.assertRaises(NoWritePermission) as ctx:
    #             self.file_checker.check_can_write_folder(self.path_desc, self.path)
    #         self.assertEqual(self.expected_msg + 'no write permission', str(ctx.exception))
