import os
import unittest
from tempfile import NamedTemporaryFile
from pathlib import Path

from chris.client import ChrisClient
from caw.movedata import upload


example_data1 = r"""
Remember, Grasshopper, falling down 1000 stairs begins by tripping over
the first one.
                -- Confusion
"""

example_data2 = r"""
The steady state of disks is full.
                -- Ken Thompson
"""


class TestUpload(unittest.TestCase):

    client = ChrisClient(
        address='http://localhost:8000/api/v1/',
        username='chris',
        password='chris1234'
    )

    def setUp(self) -> None:
        with NamedTemporaryFile(mode='w', newline='\n', encoding='utf-8', suffix='.txt',  delete=False) as tf1:
            tf1.write(example_data1)
        with NamedTemporaryFile(mode='w', newline='\n', encoding='utf-8', suffix='.txt',  delete=False) as tf2:
            tf2.write(example_data2)
        self.file1 = tf1
        self.file2 = tf2

    def tearDown(self) -> None:
        os.unlink(self.file1.name)
        os.unlink(self.file2.name)

    def test_upload(self):
        upload(
            client=self.client,
            files=[Path(self.file1.name), Path(self.file2.name)],
            parent_folder='caw/test_upload',
            upload_threads=2
        )

        results = self.client.search_uploadedfiles(fname='chris/uploads/caw/test_upload/')
        fnames = [os.path.basename(result.fname) for result in results]
        self.assertIn(os.path.basename(self.file1.name), fnames)
        self.assertIn(os.path.basename(self.file2.name), fnames)
