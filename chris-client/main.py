import models
from client import ChrisClient
from tempfile import TemporaryDirectory, NamedTemporaryFile
import os, json


client = ChrisClient(
        address='http://localhost:8000/api/v1/',
        username='chris',
        password='chris1234'
    )
#cr = client.list_compute_resources()
#cr = client.get_compute_resources_details()
#pl = client.get_plugin_details(plugin_id = 2)
#print(json.dumps(pl, sort_keys=True, indent=4))
match = client.match_compute_env('pl-s3retrieve')
#pl = client.get_plugin_resources()
