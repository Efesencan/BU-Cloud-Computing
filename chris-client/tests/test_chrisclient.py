from unittest import TestCase
import chris.models
from chris.client import ChrisClient
from tempfile import TemporaryDirectory, NamedTemporaryFile
import os


class TestChrisClient(TestCase):

    client = ChrisClient(
        address='http://localhost:8000/api/v1/',
        username='chris',
        password='chris1234'
    )

    def test_get_plugin_by_name(self):
        plugin = self.client.get_plugin(name_exact='pl-tsdircopy')
        self.assertEqual(plugin.name, 'pl-tsdircopy')

    def test_get_plugin_by_version(self):
        plugin = self.client.get_plugin(name_exact='pl-dircopy', version='2.1.0')
        self.assertEqual(plugin.name, 'pl-dircopy')
        self.assertEqual(plugin.version, '2.1.0')

    def test_get_plugin_by_url(self):
        plugin = self.client.get_plugin(url='http://localhost:8000/api/v1/plugins/2/')
        self.assertEqual(plugin.url, 'http://localhost:8000/api/v1/plugins/2/')

    def test_get_pipeline(self):
        pipeline = self.client.get_pipeline('Automatic Fetal Brain Reconstruction Pipeline')
        self.assertGreater(len(pipeline.pipings), 2)
        self.assertIn('plugin', pipeline.pipings[1])
        self.assertIn('previous', pipeline.pipings[1])

    def test_pipeline_assembly(self):
        pipeline = self.client.get_pipeline('Automatic Fetal Brain Reconstruction Pipeline')
        assembly = pipeline.assemble()
        self.assertIs(assembly.previous, None,
                      'Root of DAG has a previous plugin.')
        second = next(iter(assembly.children))
        self.assertIs(second.parent, assembly,
                      'Edge from second node to its parent is not the root.')
        counter = 0
        for _ in assembly:
            counter += 1
        self.assertEqual(counter, len(pipeline),
                         'Queue size does not match number of nodes in pipeline.')

    def test_files_pagination(self):
        chris.models.PAGINATION_LIMIT = 5
        # import logging
        # logging.basicConfig(level=logging.DEBUG)
        with TemporaryDirectory() as td:
            folder = 'chris/uploads/caw/test_files_pagination' + td
            for i in range(20):
                filename = os.path.join(td, f'{i}.txt')
                with open(filename, mode='w') as tf:
                    tf.write(f'files number {i}')

                self.client.upload(filename, folder)
            uploaded_files = self.client.search_uploadedfiles(fname=folder)
            counter = 0
            for uploaded_file in uploaded_files:
                counter += 1
                # logging.info(uploaded_file.fname)
                if counter > 20:
                    self.fail('More than 20 example files from pagination, infinite loop detected.')
        self.assertEqual(len(uploaded_files), counter)
        chris.models.PAGINATION_LIMIT = 64

    def test_download(self):
        sample_text = 'No skis take rocks like rental skis!'
        with NamedTemporaryFile(mode='w', newline='\n', encoding='utf-8', suffix='.txt', delete=False) as f:
            f.write(sample_text)

        self.client.upload(f.name, 'chris/uploads/caw/test_download')
        os.unlink(f.name)
        remote_fname = f'chris/uploads/caw/test_download/{os.path.basename(f.name)}'
        search = self.client.search_uploadedfiles(fname_exact=remote_fname)
        self.assertEqual(len(search), 1, 'Uploaded example not found.')

        uploaded_file = next(iter(search))
        uploaded_file.download(f.name)
        with open(f.name, 'r', encoding='utf-8') as downloded_file:
            lines = '\n'.join(downloded_file.readlines())
        self.assertEqual(lines, sample_text)
