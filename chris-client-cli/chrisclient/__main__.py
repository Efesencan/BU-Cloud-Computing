from click.decorators import argument
from .client import ChrisClient, PluginNotFoundError
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

@click.group()
@click.pass_context
@click.option('--username', default='chris', help='Username for ChRIS')
@click.option('--password', default='chris1234',
              help='Password for ChRIS')
@click.option('--address', default='http://'+ '128.31.26.131' +':8000/api/v1/', help='Address for ChRIS')
def main(context, username, password, address):
    context.ensure_object(dict)
    context.obj['client'] = ChrisClient(
        address=address,
        username=username,
        password=password
    )

@main.command('get_plugin_details')
@click.pass_context
@click.option('--id', '--plugin_id', default=None, help='Get a plugin\'s details from given plugin id.')
@click.option('--name', '--plugin_name', default=None, help='Get a plugin\'s details from given plugin name.')
def get_plugin_details(context, id, name):
    '''
    Get a plugin\'s details.\n
    Pass in type first (--id or --plugin_id or --name or --plugin_name) then the argument.\n
    Example: \n
    \t$ chrisclient get_plugin_details --id 1\n
    \t$ chrisclient get_plugin_details --plugin_name pl-simplefsapp
    '''
    client = context.obj['client']
    if id is not None:
        try:
                plugin_id = int(id)
        except ValueError:
            print('Invalid plugin id.')
            exit(-1)
        try:
            json_print(client.get_plugin_details(plugin_id=plugin_id))
        except PluginNotFoundError:
            print('No plugin found with that ID.')
    elif name is not None:
        plugin_name = name
        try:
            json_print(client.get_plugin_details(plugin_name=plugin_name))
        except PluginNotFoundError:
            print('No plugin found with that name.')
    else:
        print("Invalid argument. Specify '--id' or '--plugin_id' or '--name', '--plugin_name'")
        exit(-1)

@main.command('list_compute_resources')
@click.pass_context
def list_compute_resources(context):
    '''
    List all available the compute resources
    Example: \n
    \t$ chrisclient list_compute_resources
    '''
    client = context.obj['client']
    json_print(client.list_compute_resources())

@main.command('get_compute_resources_details')
@click.pass_context
def get_compute_resources_details(context):
    '''
    Get the details of all available the compute resources
    Example: \n
    \t$ chrisclient get_compute_resources_details
    '''
    client = context.obj['client']
    json_print(client.get_compute_resources_details())

@main.command('check_plugin_compute_env')
@click.pass_context
@click.argument('plugin_name')
def check_plugin_compute_env(context, plugin_name):
    '''
    Check whether the compute env is suitable for plugin.
    Pass in plugin_name
    Output: for each available compute env, output True/False indicating whether compute env satisfy the plugin requirement.\n
    If False, also output the failure reason
    Example: \n
    \t$ chrisclient check_plugin_compute_env pl-simplefsapp
    '''
    client = context.obj['client']
    try:
        json_print(client.check_plugin_compute_env(plugin_name))
    except PluginNotFoundError:
        print('No plugin found with that name.')

@main.command('list_installed_plugins')
@click.pass_context
def list_installed_plugins(context):
    '''
    List all installed plugins
    Example: \n
    \t$ chrisclient list_installed_plugins
    '''
    client = context.obj['client']
    json_print(client.list_installed_plugins())

@main.command('get_pipeline_details')
@click.pass_context
@click.argument('pipeline_id')
def get_pipeline_details(context, pipeline_id):
    '''
    Pass in pipeline_id
    Output a pipeline details.\n
    - all plugins associated with that pipeline\n
    - the topological order of plugins\n
    - the mapping from topological order to plugin_id
    Example: \n
    \t$ chrisclient get_pipeline_details 1
    '''
    client = context.obj['client']
    if pipeline_id is not None:
        json_print(client.get_pipeline_details(pipeline_id))

@main.command('match_pipeline')
@click.pass_context
@click.option('--match_type', type=click.Choice(['budget', 'env_list'], case_sensitive=False))
@click.argument('pipeline_id')
@click.argument('budget', required=False)
@click.argument('env_list', required=False)
def match_pipeline(context, match_type, pipeline_id, budget, env_list):
    '''
    Pass in: pipeline_id, budget (money in USD)\n
    Output: match each plugin in that pipeline with best expected runtime
    Example: \n
    \t$ chrisclient match_pipeline 1 --match_type=budget 1\n
    '''
    client = context.obj['client']
    try:
        pipeline_id = int(pipeline_id)
    except ValueError:
        print('Invalid pipeline_id id.')
        exit(-1)

    if match_type == 'budget':
        try:
            budget = int(budget)
        except ValueError:
            print('Invalid budget amount.')
            exit(-1)
        json_print(client.match_pipeline(pipeline_id, budget))
    elif match_type == 'env_list':
        ### TODO
        pass
    else:
        print('Invalid match_type option')
        exit(-1)


@main.command('list_all_pipelines')
@click.pass_context
def list_all_pipelines(context):
    '''
    List all available pipelines
    '''
    client = context.obj['client']
    json_print(client.list_all_pipelines())
    

def json_print(obj):
    print(json.dumps(obj, sort_keys=False, indent=4))


if __name__ == '__main__':
    main()

    # main()
