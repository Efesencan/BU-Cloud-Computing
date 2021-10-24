"""
An end-to-end test which performs the following:

1. creates a ChRIS user account.
2. caw login
3. caw search
4. caw upload --pipeline ...
5. caw download
6. caw logout
"""

import os
import unittest

import random
import string
import requests
import subprocess as sp
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import sleep
from glob import iglob


def random_string(length=12) -> str:
    return ''.join(random.choice(string.ascii_letters) for x in range(length))


address = 'http://localhost:8000/api/v1/'
username = 'caw_test_' + random_string(6)
password = random_string(12)


def create_account():
    res = requests.post(
        f'{address}users/',
        headers={
            'Content-Type': 'application/vnd.collection+json',
            'Accept': 'application/json'
        },
        json={
            'template': {
                'data': [
                    {
                        'name': 'email',
                        'value': f'{username}@babyMRI.org'
                    },
                    {
                        'name': 'username',
                        'value': username
                    },
                    {
                        'name': 'password',
                        'value': password
                    }
                ]
            }
        }
    )
    res.raise_for_status()
    data = res.json()

    assert 'username' in data
    assert data['username'] == username


def poll_feed(feed_url: str, jobs_count: int, poll_interval=10, timeout=300) -> dict:
    timer = 0
    headers = {
        'Accept': 'application/json'
    }
    data = {}
    while timer <= timeout:
        res = requests.get(feed_url, headers=headers, auth=(username, password))
        res.raise_for_status()
        data = res.json()
        if data['finished_jobs'] == jobs_count:
            return data
        sleep(poll_interval)
        timer += poll_interval
    return data


class TestEndToEnd(unittest.TestCase):
    @unittest.skipUnless('CAW_TEST_FULL' in os.environ, 'Set CAW_TEST_FULL=y to run the end-to-end test.')
    def test_endtoend(self):
        create_account()

        sp.run(['caw', '--address', address, '--username', username, 'login', '--password-stdin'],
               input=(password + '\n'), text=True, check=True)

        with NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
            f.write("If you steal from one author it's plagiarism; if you steal from"
                    "\nmany it's research."
                    '\n                -- Wilson Mizner\n')

        search = sp.check_output(['caw', 'search'], text=True)
        self.assertIn('Example branching pipeline', search,
                      msg='"Example branching pipeline" not found in `caw search`')

        feed_url = sp.check_output(['caw', 'upload', '--pipeline', 'Example branching pipeline', '--', f.name],
                                   text=True)
        self.assertTrue(feed_url.startswith(address),
                        msg='Feed URL was not correctly printed after `caw upload`')

        feed_data = poll_feed(feed_url, jobs_count=9)

        with TemporaryDirectory() as tmpdir:
            sp.run(['caw', 'download', feed_data['files'], tmpdir])
            # the pipeline runs pl-dircopy --prefix L where L is a letter.
            # if the DAG is constructed properly, it should produce the following prefixes
            prefixes = {'', 'a', 'ba', 'ca', 'dba', 'eca', 'fca', 'gca', 'hgca'}
            suffix = os.path.basename(f.name)
            results = [
                # example:
                # '/tmp/folder/caw_test_SzvEhj/feed_10/pl-dircopy_81/pl-simpledsapp_82/pl-simpledsapp_83/pl-simpledsapp_85/data/fcatmpl_hy4m5o.txt'
                # --> 'fca'
                os.path.basename(fname[:-len(suffix)])
                for fname in iglob(os.path.join(tmpdir, '**', '*' + suffix), recursive=True)
            ]
            self.assertEqual(len(results), 9, msg='Incorrect number of files produced by feed.')
            self.assertSetEqual(prefixes, set(results),
                                msg='DAG not reconstructed in the correct order.')
        sp.run(['caw', 'logout'])


if __name__ == '__main__':
    unittest.main()
