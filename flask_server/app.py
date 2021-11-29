from sys import is_finalizing
from flask import Flask, request, session
from client import ChrisClient, PipelineNotFoundError, PluginNotFoundError
#import click

class store():
    client = None

data_store = store()

app = Flask(__name__)

@app.route('/')
def hello():
    return 'server is online'

@app.route('/api/login', methods=['POST'])
def login():
    request_json = request.get_json()
    address = request_json.get('address')
    username = request_json.get('username')
    password = request_json.get('password')
    data_store.client = ChrisClient(address=address, username=username, password=password)
    if data_store.client is not None:
        return "success"
    else:
        return "failed"

@app.route('/api/get_plugin_details', methods=['POST'])
def get_plugin_details():
    request_json = request.get_json()
    id = request_json.get('id')
    name = request_json.get('name')
    client = data_store.client
    if id is not None:
        try:
            plugin_id = int(id)
        except ValueError:
            return('Invalid plugin id.')
        try:
            return client.get_plugin_details(plugin_id=plugin_id)
        except PluginNotFoundError:
            print('No plugin found with that ID.')
    elif name is not None:
        plugin_name = name
        try:
            return client.get_plugin_details(plugin_name=plugin_name)
        except PluginNotFoundError:
            return('No plugin found with that name')
    else:
        return('Invalid argument.')

@app.route('/api/list_compute_resources', methods=['POST'])
def list_compute_resources():
    client = data_store.client
    return(client.list_compute_resources())

@app.route('/api/get_compute_resources_details', methods=['POST'])
def get_compute_resources_details():
    client = data_store.client
    return(client.get_compute_resources_details())

@app.route('/api/check_plugin_compute_env', methods=['POST'])
def check_plugin_compute_env():
    request_json = request.get_json()
    plugin_name = request_json.get('plugin_name')
    client = data_store.client
    try:
        return client.check_plugin_compute_env(plugin_name)
    except PluginNotFoundError:
        return "No plug-in found with that name"

@app.route('/api/check_pipeline_compute_env', methods=['POST'])
def check_pipeline_compute_env():
    client = data_store.client
    request_json = request.get_json()
    id = request_json.get('pipeline_id')
    pipeline_name = request_json.get('pipeline_name')
    if id is not None:
        try:
            pipeline_id = int(id)
        except ValueError:
            return "Invalid pipeline id"
        try:
            return client.check_pipeline_compute_env(pipeline_id=pipeline_id)
        except PipelineNotFoundError:
            return "No pipeline found with this id"
    elif pipeline_name is not None:
        try:
            client.check_pipeline_compute_env(pipeline_id=client.pipeline_name_to_id(plugin_name))
        except PipelineNotFoundError:
            return "No pipeline found with that name"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port="4000", debug=True)