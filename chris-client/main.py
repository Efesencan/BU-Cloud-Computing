import models
from client import ChrisClient
from tempfile import TemporaryDirectory, NamedTemporaryFile
import os


client = ChrisClient(
        address='http://localhost:8000/api/v1/',
        username='chris',
        password='chris1234'
    )
#cr = client.list_compute_resources()
#cr = client.get_compute_resources_details()
pl = client.get_plugin_details(plugin_id = None, plugin_name = "pl-s3retrieve")
