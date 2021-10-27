from .client import ChrisClient
import click
import json


# client = ChrisClient(
#         address='http://localhost:8000/api/v1/',
#         username='chris',
#         password='chris1234'
#     )
# #cr = client.list_compute_resources()
# cr = client.get_compute_resources_details()
# pl = client.get_plugin_details(plugin_id = 2)
# print(pl)
# #print(json.dumps(pl, sort_keys=True, indent=4))
# match = client.check_plugin_compute_env('pl-s3retrieve')
# #pl = client.get_plugin_resources()

@click.command()
@click.option('--username', default='chris', help='Username for ChRIS')
@click.option('--password', default='chris1234',
              help='Password for ChRIS')
@click.option('--address', default='http://localhost:8000/api/v1/', help='Address for ChRIS')
@click.option('--get_plugin_details', nargs=2, type=(str, str), default=(None, None), help='Get a plugin\'s details. Pass in type first (plugin_id or plugin_name) then the argument.')
@click.option('--list_compute_resources', is_flag=True, help='List the compute resources')
@click.option('--get_compute_resources_details', is_flag=True,  help='Get the details of the compute resource')
@click.option('--check_plugin_compute_env', default='', help='Check whether the compute env is suitable for plugin. Pass in plugin_name')
@click.option('--list_installed_plugins', is_flag=True,  help='List the installed plugins')
def main(username, password, address, list_compute_resources, get_compute_resources_details, list_installed_plugins,
         get_plugin_details, check_plugin_compute_env):
    client = ChrisClient(
        address=address,
        username=username,
        password=password
    )
    if get_plugin_details:
        type_search, argument = get_plugin_details
        if type_search == 'plugin_id':
            try:
                plugin_id = int(argument)
            except ValueError:
                print('Invalid plugin id.')
            json_print(client.get_plugin_details(plugin_id=plugin_id))
        elif type_search == 'plugin_name':
            plugin_name = argument
            json_print(client.get_plugin_details(plugin_name=plugin_name))

    if list_compute_resources:
        json_print(client.get_compute_resources_details())

    if get_compute_resources_details:
        json_print(client.get_compute_resources_details())

    if check_plugin_compute_env:
        json_print(client.check_plugin_compute_env(check_plugin_compute_env))

    if list_installed_plugins:
        json_print(client.list_installed_plugins())


def json_print(obj):
    print(json.dumps(obj, sort_keys=True, indent=4))


if __name__ == '__main__':
    main()
