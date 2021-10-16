import models
from client import ChrisClient
from tempfile import TemporaryDirectory, NamedTemporaryFile
import os


client = ChrisClient(
        address='http://10.0.4.213:8000/api/v1/',
        username='chris',
        password='chris1234'
    )
cr = client.list_compute_resoures()

