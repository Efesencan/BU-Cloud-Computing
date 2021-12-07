from os import path
# from click import exceptions
import requests
from typing import Optional, Set, Union, Dict
import json

from .cli_models import PluginInstance, Plugin, Pipeline, UploadedFiles, Feed, ComputeResource

# import networkx as nx
### for debugging
import math


class ChrisClientError(Exception):
    pass


class ChrisIncorrectLoginError(ChrisClientError):
    pass


class ChrisResourceNotFoundError(ChrisClientError):
    pass


class PluginNotFoundError(ChrisResourceNotFoundError):
    pass


class PipelineNotFoundError(ChrisResourceNotFoundError):
    pass


class ChrisClient:
    def __init__(self, address: str, username: Optional[str] = None, password: Optional[str] = None,
                 token: Optional[str] = None):
        """
        Log into ChRIS.
        :param address: CUBE address
        :param username: account username
        :param password: account password
        :param token: use token authorization, takes priority over basic authorization
        """
        if not address.endswith('/api/v1/'):
            raise ValueError('Address of CUBE must end with "/api/v1/"')
        self.addr = address
        self.search_addr_plugins = address + 'plugins/search/'
        self.search_addr_plugins_instances = address + 'plugins/instances/search/'
        self.search_addr_pipelines = address + 'pipelins/search/'
        self.addr_compute_resources = address + 'computeresources/'

        self._s = requests.Session()
        self._s.headers.update({'Accept': 'application/json'})

        if not token:
            if not username or not password:
                raise ChrisIncorrectLoginError('Username and password are required.')

            auth_url = self.addr + 'auth-token/'
            login = self._s.post(auth_url, json={
                'username': username,
                'password': password
            })
            if login.status_code == 400:
                res = login.json()
                raise ChrisIncorrectLoginError(res['non_field_errors'][0] if 'non_field_errors' in res else login.text)
            login.raise_for_status()
            token = login.json()['token']

        self._s.headers.update({
            'Content-Type': 'application/vnd.collection+json',
            'Authorization': 'Token ' + token
        })
        self.token = token
        """
        HTTP basic authentication token.
        """

        res = self._s.get(address)
        if res.status_code == 401:
            data = res.json()
            raise ChrisIncorrectLoginError(data['detail'] if 'detail' in data else res.text)
        if res.status_code != 200:
            raise ChrisClientError(f'CUBE response status code was {res.status_code}.')
        res.raise_for_status()
        data = res.json()
        if 'collection_links' not in data or 'uploadedfiles' not in data['collection_links']:
            raise ChrisClientError(f'Unexpected CUBE response: {res.text}')
        self.collection_links = data['collection_links']

        res = self._s.get(self.collection_links['user'])
        res.raise_for_status()
        data = res.json()
        self.username = data['username']
        """
        The ChRIS user's username.
        """

    def upload(self, file_path: str, upload_folder: str):
        """
        Upload a local file into ChRIS backend Swift storage.
        :param file_path: local file path
        :param upload_folder: path in Swift where to upload to
        :return: response
        """
        bname = path.basename(file_path)
        upload_path = path.join(upload_folder, bname)

        with open(file_path, 'rb') as file_object:
            files = {
                'upload_path': (None, upload_path),
                'fname': (bname, file_object)
            }
            res = self._s.post(
                self.collection_links['uploadedfiles'],
                files=files,
                headers={
                    'Accept': 'application/vnd.collection+json',
                    'Content-Type': None
                }
            )
        res.raise_for_status()
        return res.json()

    def _url2plugin(self, url):
        res = self._s.get(url)
        res.raise_for_status()
        return Plugin(**res.json(), session=self._s)

    def get_plugin(self, name_exact='', version='', url='') -> Plugin:
        """
        Get a single plugin, either searching for it by its exact name, or by URL.
        :param name_exact: name of plugin
        :param version: (optional) version of plugin
        :param url: (alternative to name_exact) url of plugin
        :return:
        """
        if name_exact:
            search = self.search_plugin(name_exact, version)
            return search.pop()
        elif url:
            return self._url2plugin(url)
        else:
            raise ValueError('Must give either plugin name or url')

    def search_plugin(self, name_exact: str, version: '') -> Set[Plugin]:
        payload = {
            'name_exact': name_exact
        }
        if version:
            payload['version'] = version
        res = self._s.get(self.search_addr_plugins, params=payload)
        res.raise_for_status()
        data = res.json()
        if data['count'] < 1:
            raise PluginNotFoundError(name_exact)
        return set(Plugin(**pldata, session=self._s) for pldata in data['results'])

    def get_plugin_instance(self, id: Union[int, str]):
        """
        Get a plugin instance.
        :param id: Either a plugin instance ID or URL
        :return: plugin instance
        """
        res = self._s.get(id if '/' in id else f'{self.addr}plugins/instances/{id}/')
        res.raise_for_status()
        return PluginInstance(**res.json())

    def run(self, plugin_name='', plugin_url='', plugin: Optional[PluginInstance] = None,
            params: Optional[dict] = None) -> PluginInstance:
        """
        Create a plugin instance. Either procide a plugin object,
        or search for a plugin by name or URL.
        :param plugin: plugin to run
        :param plugin_name: name of plugin to run
        :param plugin_url: alternatively specify plugin URL
        :param params: plugin parameters as key-value pairs (not collection+json)
        :return:
        """
        if not plugin:
            plugin = self.get_plugin(name_exact=plugin_name, url=plugin_url)
        return plugin.create_instance(params)

    def search_uploadedfiles(self, fname='', fname_exact='') -> UploadedFiles:
        query = {
            'fname': fname,
            'fname_exact': fname_exact
        }
        qs = '&'.join([f'{k}={v}' for k, v in query.items() if v])
        url = f"{self.collection_links['uploadedfiles']}search/?{qs}"
        return self.get_uploadedfiles(url)

    def get_uploadedfiles(self, url: str) -> UploadedFiles:
        return UploadedFiles(url=url, session=self._s)

    def search_pipelines(self, name='') -> Set[Pipeline]:
        payload = {
            'name': name
        }
        res = self._s.get(self.collection_links['pipelines'] + 'search/', params=payload)
        res.raise_for_status()
        data = res.json()
        return set(Pipeline(**p, session=self._s) for p in data['results'])

    def get_pipeline(self, name: str) -> Pipeline:
        search = self.search_pipelines(name)
        if not search:
            raise PipelineNotFoundError(name)
        return search.pop()

    def list_compute_resources(self) -> Dict[str, list]:
        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        data = res.json()
        all_cr = set(ComputeResource(**p, session=self._s) for p in data['results'])
        dict_cr = {}
        list_cr = []
        for cr in all_cr:
            list_cr.append(cr.name)
        dict_cr["compute_resources"] = list_cr
        # print(json.dumps(dict_cr, sort_keys=True, indent=4))
        return dict_cr

    def get_compute_resources_details(self) -> Dict[str, Dict]:
        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        data = res.json()
        compute_resources = data['results']
        dict_cr = {}
        for resource in compute_resources:
            dict_cr[resource['name']] = resource
        # print(json.dumps(dict_cr, sort_keys=True, indent=4))
        return dict_cr

    def list_installed_plugins(self) -> Dict[str, list]:
        res = self._s.get(self.search_addr_plugins)
        res.raise_for_status()
        data = res.json()
        plugins = data['results']
        plugin_names = {'plugins': []}
        for plugin in plugins:
            plugin_name = plugin['name']
            plugin_names['plugins'].append(plugin_name)
        # print(json.dumps(plugin_names, sort_keys=True, indent=4))
        return plugin_names

    def get_plugin_details(self, plugin_id=None, plugin_name=None):
        res = self._s.get(self.search_addr_plugins)
        res.raise_for_status()
        data = res.json()
        if plugin_id is None and plugin_name is None:
            # print(json.dumps(data, sort_keys=True, indent=4))
            return data
        plugins = data['results']
        dict_plugin = {}
        if plugin_id is not None:
            for plugin in plugins:
                if plugin['id'] == plugin_id:
                    dict_plugin[plugin['name']] = plugin

        elif plugin_name is not None:
            for plugin in plugins:
                if plugin['name'] == plugin_name:
                    dict_plugin[plugin['name']] = plugin

        if len(dict_plugin) == 0:
            raise PluginNotFoundError()
        # print(json.dumps(dict_plugin, sort_keys=True, indent=4))
        return dict_plugin

    def check_plugin_compute_env(self, plugin_name, summary=False):
        plugin_details = self.get_plugin_details(plugin_name=plugin_name)
        compute_addr = plugin_details[plugin_name]['compute_resources']
        min_cpu_limit = plugin_details[plugin_name]['min_cpu_limit']
        min_gpu_limit = plugin_details[plugin_name]['min_gpu_limit']
        min_memory_limit = plugin_details[plugin_name]['min_memory_limit']
        min_number_of_workers = plugin_details[plugin_name]['min_number_of_workers']

        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        data = res.json()
        # print(json.dumps(data, sort_keys=True, indent=4))
        compute_resources = data['results']
        match_dict = {}
        match_list = []
        match_dict['plugin_name'] = plugin_name

        resource_count = 0
        prev_resource = ''
        pass_count = 0
        pass_list = []
        for resource in compute_resources:
            if resource['name'] in ['auto_free', 'auto_best']:
                # don't check against 'auto' option
                continue
            cmp_cpu = resource['cpus']
            cmp_gpu = resource['gpus']
            cmp_cost = resource['cost']
            cmp_mem = resource['memory']
            cmp_worker = resource['workers']
            fail_count = 0
            if cmp_cpu < min_cpu_limit:
                fail_count = fail_count + 1
                message = f"{str(min_cpu_limit)} milli-core CPU's, but {str(cmp_cpu)} milli-core CPUs available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_gpu < min_gpu_limit:
                fail_count = fail_count + 1
                message = f"{str(min_gpu_limit)} milli-core GPU's, but {str(cmp_gpu)} milli-core GPUs available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_mem < min_memory_limit:
                fail_count = fail_count + 1
                message = f"{str(min_memory_limit)} MB's memory, but {str(cmp_mem)} MB's available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_worker < min_number_of_workers:
                fail_count = fail_count + 1
                message = f"{str(min_number_of_workers)} workers, but only {str(cmp_worker)} workers available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_cpu >= min_cpu_limit and cmp_gpu >= min_gpu_limit and cmp_mem >= min_memory_limit and cmp_worker >= min_number_of_workers:
                pass_count = pass_count + 1
                match_list.append({resource['name']: {'fit': True}})
                pass_list.append(resource['name'])
            resource_count += 1
            # else:
            #    match_list.append({resource['name']: {'fit': False, 'message': 'Not enough cpu'}})
        match_dict['matching'] = match_list

        # print(json.dumps(match_dict, sort_keys=True, indent=4))
        # print("building message")
        message = ""
        # print(json.dumps(compute_resources, sort_keys=True, indent=4))
        if summary == True:
            # for index, resource in enumerate(compute_resources):
            #     print("message = %s" %  match_list[index][resource['name']]['message'])
            #     # message = message + "%s : %s\n" % (resource, match_list[index][resource['name']]['message'])
            #     print("index = %s" %  index)
            # message = match_dict['matching']
            message = json.dumps(match_dict['matching'], sort_keys=True, indent=4)
            return match_dict, (pass_count > 0), message, pass_list
        return match_dict

    def check_pipeline_compute_env(self, pipeline_id, env_list=None):
        res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
        res.raise_for_status()
        data = res.json()

        res = self._s.get(data['plugins'])
        res.raise_for_status()
        data = res.json()
        plugin_list = data['results']
        return_dict = {}
        total_pass = True
        fail_plugin = []
        detail_list = []
        for plugin in plugin_list:
            # print(plugin['name'])
            detail, pass_check = self.check_plugin_compute_env(plugin_name=plugin['name'], summary=True)
            ### total_pass will fail if only one of plugin fail to run
            detail_list.append(detail)
            if pass_check == False:
                fail_plugin = detail["plugin_name"]
            total_pass = total_pass and pass_check

        return_dict["fit"] = total_pass
        return_dict["fail case"] = fail_plugin
        return_dict["details"] = detail_list
        return return_dict


    # def get_pipeline_details(self, pipeline_id: int):
    #     return_dict = {}
    #     ### get pipeline json object from database
    #     res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
    #     res.raise_for_status()
    #     data = res.json()

    #     ### get plugins topography from database
    #     res_topo = self._s.get(data['plugin_pipings'])
    #     res_topo.raise_for_status()
    #     data_topo = res_topo.json()
    #     ### networkx graph object
    #     G = nx.DiGraph()
    #     link_list = data_topo['results']
    #     identity_dict = {} ### keep track of which node_id is corresponding to which plugin id
    #     for link in link_list:
    #         identity_dict[link['id']] = link['plugin_id']
    #         if 'previous_id' in link:
    #             previous_label = link['previous_id']
    #             this_label = link['id']
    #             G.add_edge(previous_label, this_label)
    #     topolopy = list(nx.topological_sort(G)) ### list of node_id dictating which node come first
    #     plugin_id_topo = [identity_dict[k] for k in topolopy]


    #     ### get list of plugins associated with that pipeline json object from database
    #     res = self._s.get(data['plugins'])
    #     res.raise_for_status()
    #     data = res.json()

    #     plugin_list = data['results']
    #     # pp = pprint.PrettyPrinter(indent=4)
    #     # pp.pprint(data)

    #     ### extract information from each plugins
    #     return_dict['status'] = 'OK'
    #     return_dict['plugin_list'] = []
    #     for plugin in plugin_list:
    #         # print(plugin)
    #         current_plugin = {}
    #         current_plugin['plugin_id'] = plugin['id']
    #         current_plugin['plugin_name'] = plugin['name']
    #         return_dict['plugin_list'].append(current_plugin)
    #     return_dict['topology_nodeid'] = topolopy
    #     return_dict['topology'] = plugin_id_topo
    #     return_dict['mapping'] = identity_dict
    #     # print(return_dict)
    #     return return_dict
    ###
    # def match_pipeline(self, pipeline_id: int, budget: int = 0):
    #     '''
    #     overview:
    #         takes in pipeline_id, budget and compute how to assign each plug-in to acheive lowest runtime while staying under budget
    #     input:
    #         pipeline_id = id of the pipeline to be processed\n
    #         budget = amount of availiable cost that constrain the compute environment assignment
    #     output: a dictionary with list of compute environment assignment
    #     '''
    #     return_dict = {}

    #     ### 1. get all plug-in id from the given pipeline
    #     data = self.get_pipeline_details(pipeline_id)
    #     plugin_list = data['plugin_list']

    #     ### 1.2 get all compute env cost
    #     res = self._s.get(self.addr_compute_resources)
    #     res.raise_for_status()
    #     env_data = res.json()
    #     cost_dict = {}
    #     compute_resources = env_data['results']
    #     for i, env in enumerate(compute_resources):
    #         cost_dict[env['name']] = env['cost']
    #         cost_dict[i] = env['cost']
    #         # cmp_cost = resource['cost']
    #     # print(cost_dict)
    #     ### 2. for each plug-in get the expected runtime and cost
    #     ###
    #     runtime_dict = {}
    #     for plugin in plugin_list:
    #         runtime_dict[plugin['plugin_id']] = {}
    #         for i, env in enumerate(compute_resources):
    #             expected_runtime = 100 # this should be changed to input size
    #             ### need to change how we calculate expected_runtime
    #             expected_runtime = expected_runtime / (env['cpus']+0.001)
    #             ###
    #             runtime_dict[plugin['plugin_id']][env['name']] = expected_runtime
    #             runtime_dict[plugin['plugin_id']][i] = expected_runtime
    #     # print(runtime_dict)
    #     # print(runtime_dict['pl-s3retrieve']['test_env1'])
    #     ### 3. construct a network where node = current plug-in, edge = the environment to take, weight = expected runtime
    #     print("node sequence: ", data['topology'])
    #     print("plugin sequence: ", [plugin['plugin_name'] for plugin in data['plugin_list']])
    #     G = nx.DiGraph()
    #     count = 0
    #     num_env = len(compute_resources)
    #     pos = {}
    #     pos[0] = (0,0)
    #     for n in range(0, len(data['topology'])):

    #         ### 1st layer
    #         # print("layer ", n)
    #         if count == 0:
    #             for i, env in enumerate(compute_resources):
    #                 ### DO REQUIREMENT CHECK HERE
    #                 ### if check fail don't add edge

    #                 G.add_edge(count, (count+i+1), weight=env['cost'])
    #                 pos[count+i+1] = (1,i)
    #                 # print((1,i))
    #             count = count + 1
    #         ### 2nd and next layer
    #         else:
    #             for i, env in enumerate(compute_resources):
    #                 for j, env2 in enumerate(compute_resources):
    #                     ### DO REQUIREMENT CHECK HERE
    #                     ### if check fail don't add edge

    #                     G.add_edge(count+i, count+num_env+j, weight=env2['cost'])
    #                     pos[count+num_env+j] = (math.ceil(count/num_env)+1,j)
    #                     # print("edge: ", (count+i, count+num_env+j))
    #                     # print((math.ceil(count/num_env)+1,j))
    #             count = count + num_env
    #     ### last layer
    #     # print("last layer")
    #     for i, env in enumerate(compute_resources):
    #         ### DO REQUIREMENT CHECK HERE
    #         ### if check fail don't add edge

    #         G.add_edge(count+i, count+num_env, weight=0)
    #     pos[count+i+1] = (math.ceil(count/num_env)+1,0)
    #     count = count + num_env
    #     ### use next 2 lines to print what's the network looks like
    #     # nx.draw(G, pos=pos)
    #     # plt.show()
    #     ### 3.1 calculate all possible path
    #     best_path_time = -1
    #     best_path_cost = -1
    #     best_path = []
    #     ### for each path, calculate total expected runtime and total cost
    #     for path in nx.all_simple_paths(G, source=0, target=count):

    #         # print(path[:-1])
    #         # get total expected time
    #         total_time = 0
    #         total_cost = 0
    #         for i,v in enumerate(path[:-2]):
    #             next_node = path[i+1]
    #             which_plugin = data['topology'][i]
    #             env_index = cost_dict[(next_node -1) % num_env]
    #             total_time = total_time + runtime_dict[which_plugin][env_index]
    #             total_cost = total_cost + cost_dict[env_index]
    #             # if v == 0:
    #             #     total_time = total_time + runtime_dict[which_plugin][cost_dict[next_node % num_env]]
    #             # else:
    #             #     total_time = total_time + runtime_dict[which_plugin][cost_dict[int(next_node-this_node-num_env)]]

    #             # print(path)
    #         # print(path[:-1])
    #         # print('total time = ', total_time)
    #         # print('total cost =', total_cost)
    #         ### replace the current best path if it doesn't go over budget and any of the following is true
    #         ### 1. there's no best path yet
    #         ### 2. current path has better time
    #         ### 3. current path has same time but with lower cost
    #         if total_cost <= budget:
    #             if total_time < best_path_time or best_path_time == -1:
    #                 best_path_time = total_time
    #                 best_path_cost = total_cost
    #                 best_path = path
    #             if total_time == best_path_time and total_cost< best_path_cost:
    #                 best_path_time = total_time
    #                 best_path_cost = total_cost
    #                 best_path = path



    #     # print("best path:", best_path)


    def check_plugin_compute_env(self, plugin_name, summary=False):
        plugin_details = self.get_plugin_details(plugin_name=plugin_name)
        compute_addr = plugin_details[plugin_name]['compute_resources']
        min_cpu_limit = plugin_details[plugin_name]['min_cpu_limit']
        min_gpu_limit = plugin_details[plugin_name]['min_gpu_limit']
        min_memory_limit = plugin_details[plugin_name]['min_memory_limit']
        min_number_of_workers = plugin_details[plugin_name]['min_number_of_workers']

        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        data = res.json()
        # print(json.dumps(data, sort_keys=True, indent=4))
        compute_resources = data['results']
        match_dict = {}
        match_list = []
        match_dict['plugin_name'] = plugin_name

        resource_count = 0
        prev_resource = ''
        pass_count = 0
        pass_list = []
        for resource in compute_resources:
            if resource['name'] in ['auto_free', 'auto_best']:
                # don't check against 'auto' option
                continue
            cmp_cpu = resource['cpus']
            cmp_gpu = resource['gpus']
            cmp_cost = resource['cost']
            cmp_mem = resource['memory']
            cmp_worker = resource['workers']
            fail_count = 0
            if cmp_cpu < min_cpu_limit:
                fail_count = fail_count + 1
                message = f"{str(min_cpu_limit)} CPU's, but {str(cmp_cpu)} CPUs available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_gpu < min_gpu_limit:
                fail_count = fail_count + 1
                message = f"{str(min_gpu_limit)} GPU's, but {str(cmp_gpu)} GPUs available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_mem < min_memory_limit:
                fail_count = fail_count + 1
                message = f"{str(min_memory_limit)} MB's memory, but {str(cmp_mem)} MB's available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_worker < min_number_of_workers:
                fail_count = fail_count + 1
                message = f"{str(min_number_of_workers)} workers, but only {str(cmp_worker)} workers available."
                if resource['name'] == prev_resource:
                    match_list[resource_count][resource['name']]['message'].append(message)
                else:
                    match_list.append({resource['name']: {'fit': False, 'message': [message]}})
                    prev_resource = resource['name']
            if cmp_cpu >= min_cpu_limit and cmp_gpu >= min_gpu_limit and cmp_mem >= min_memory_limit and cmp_worker >= min_number_of_workers:
                pass_count = pass_count + 1
                match_list.append({resource['name']: {'fit': True}})
                pass_list.append(resource['name'])
            resource_count += 1
            # else:
            #    match_list.append({resource['name']: {'fit': False, 'message': 'Not enough cpu'}})
        match_dict['matching'] = match_list

        # print(json.dumps(match_dict, sort_keys=True, indent=4))
        # print("building message")
        message = ""
        # print(json.dumps(compute_resources, sort_keys=True, indent=4))
        if summary == True:
            # for index, resource in enumerate(compute_resources):
            #     print("message = %s" %  match_list[index][resource['name']]['message'])
            #     # message = message + "%s : %s\n" % (resource, match_list[index][resource['name']]['message'])
            #     print("index = %s" %  index)
            # message = match_dict['matching']
            message = json.dumps(match_dict['matching'], sort_keys=True, indent=4)
            return match_dict, (pass_count > 0), message, pass_list
        return match_dict


    def check_pipeline_compute_env(self, pipeline_id, env_list=None):
        res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
        res.raise_for_status()
        data = res.json()

        res = self._s.get(data['plugins'])
        res.raise_for_status()
        data = res.json()
        plugin_list = data['results']
        return_dict = {}
        total_pass = True
        fail_plugin = []
        detail_list = []
        for plugin in plugin_list:
            # print(plugin['name'])
            detail, pass_check = self.check_plugin_compute_env(plugin_name=plugin['name'], summary=True)
            ### total_pass will fail if only one of plugin fail to run
            detail_list.append(detail)
            if pass_check == False:
                fail_plugin = detail["plugin_name"]
            total_pass = total_pass and pass_check

        return_dict["fit"] = total_pass
        return_dict["fail case"] = fail_plugin
        return_dict["details"] = detail_list
        return return_dict


        # def get_pipeline_details(self, pipeline_id: int):
        #     return_dict = {}
        #     ### get pipeline json object from database
        #     res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
        #     res.raise_for_status()
        #     data = res.json()

        #     ### get plugins topography from database
        #     res_topo = self._s.get(data['plugin_pipings'])
        #     res_topo.raise_for_status()
        #     data_topo = res_topo.json()
        #     ### networkx graph object
        #     G = nx.DiGraph()
        #     link_list = data_topo['results']
        #     identity_dict = {} ### keep track of which node_id is corresponding to which plugin id
        #     for link in link_list:
        #         identity_dict[link['id']] = link['plugin_id']
        #         if 'previous_id' in link:
        #             previous_label = link['previous_id']
        #             this_label = link['id']
        #             G.add_edge(previous_label, this_label)
        #     topolopy = list(nx.topological_sort(G)) ### list of node_id dictating which node come first
        #     plugin_id_topo = [identity_dict[k] for k in topolopy]


        #     ### get list of plugins associated with that pipeline json object from database
        #     res = self._s.get(data['plugins'])
        #     res.raise_for_status()
        #     data = res.json()

        #     plugin_list = data['results']
        #     # pp = pprint.PrettyPrinter(indent=4)
        #     # pp.pprint(data)

        #     ### extract information from each plugins
        #     return_dict['status'] = 'OK'
        #     return_dict['plugin_list'] = []
        #     for plugin in plugin_list:
        #         # print(plugin)
        #         current_plugin = {}
        #         current_plugin['plugin_id'] = plugin['id']
        #         current_plugin['plugin_name'] = plugin['name']
        #         return_dict['plugin_list'].append(current_plugin)
        #     return_dict['topology_nodeid'] = topolopy
        #     return_dict['topology'] = plugin_id_topo
        #     return_dict['mapping'] = identity_dict
        #     # print(return_dict)
        #     return return_dict
        ###
        # def match_pipeline(self, pipeline_id: int, budget: int = 0):
        #     '''
        #     overview:
        #         takes in pipeline_id, budget and compute how to assign each plug-in to acheive lowest runtime while staying under budget
        #     input:
        #         pipeline_id = id of the pipeline to be processed\n
        #         budget = amount of availiable cost that constrain the compute environment assignment
        #     output: a dictionary with list of compute environment assignment
        #     '''
        #     return_dict = {}

        #     ### 1. get all plug-in id from the given pipeline
        #     data = self.get_pipeline_details(pipeline_id)
        #     plugin_list = data['plugin_list']

        #     ### 1.2 get all compute env cost
        #     res = self._s.get(self.addr_compute_resources)
        #     res.raise_for_status()
        #     env_data = res.json()
        #     cost_dict = {}
        #     compute_resources = env_data['results']
        #     for i, env in enumerate(compute_resources):
        #         cost_dict[env['name']] = env['cost']
        #         cost_dict[i] = env['cost']
        #         # cmp_cost = resource['cost']
        #     # print(cost_dict)
        #     ### 2. for each plug-in get the expected runtime and cost
        #     ###
        #     runtime_dict = {}
        #     for plugin in plugin_list:
        #         runtime_dict[plugin['plugin_id']] = {}
        #         for i, env in enumerate(compute_resources):
        #             expected_runtime = 100 # this should be changed to input size
        #             ### need to change how we calculate expected_runtime
        #             expected_runtime = expected_runtime / (env['cpus']+0.001)
        #             ###
        #             runtime_dict[plugin['plugin_id']][env['name']] = expected_runtime
        #             runtime_dict[plugin['plugin_id']][i] = expected_runtime
        #     # print(runtime_dict)
        #     # print(runtime_dict['pl-s3retrieve']['test_env1'])
        #     ### 3. construct a network where node = current plug-in, edge = the environment to take, weight = expected runtime
        #     print("node sequence: ", data['topology'])
        #     print("plugin sequence: ", [plugin['plugin_name'] for plugin in data['plugin_list']])
        #     G = nx.DiGraph()
        #     count = 0
        #     num_env = len(compute_resources)
        #     pos = {}
        #     pos[0] = (0,0)
        #     for n in range(0, len(data['topology'])):

        #         ### 1st layer
        #         # print("layer ", n)
        #         if count == 0:
        #             for i, env in enumerate(compute_resources):
        #                 ### DO REQUIREMENT CHECK HERE
        #                 ### if check fail don't add edge

        #                 G.add_edge(count, (count+i+1), weight=env['cost'])
        #                 pos[count+i+1] = (1,i)
        #                 # print((1,i))
        #             count = count + 1
        #         ### 2nd and next layer
        #         else:
        #             for i, env in enumerate(compute_resources):
        #                 for j, env2 in enumerate(compute_resources):
        #                     ### DO REQUIREMENT CHECK HERE
        #                     ### if check fail don't add edge

        #                     G.add_edge(count+i, count+num_env+j, weight=env2['cost'])
        #                     pos[count+num_env+j] = (math.ceil(count/num_env)+1,j)
        #                     # print("edge: ", (count+i, count+num_env+j))
        #                     # print((math.ceil(count/num_env)+1,j))
        #             count = count + num_env
        #     ### last layer
        #     # print("last layer")
        #     for i, env in enumerate(compute_resources):
        #         ### DO REQUIREMENT CHECK HERE
        #         ### if check fail don't add edge

        #         G.add_edge(count+i, count+num_env, weight=0)
        #     pos[count+i+1] = (math.ceil(count/num_env)+1,0)
        #     count = count + num_env
        #     ### use next 2 lines to print what's the network looks like
        #     # nx.draw(G, pos=pos)
        #     # plt.show()
        #     ### 3.1 calculate all possible path
        #     best_path_time = -1
        #     best_path_cost = -1
        #     best_path = []
        #     ### for each path, calculate total expected runtime and total cost
        #     for path in nx.all_simple_paths(G, source=0, target=count):

        #         # print(path[:-1])
        #         # get total expected time
        #         total_time = 0
        #         total_cost = 0
        #         for i,v in enumerate(path[:-2]):
        #             next_node = path[i+1]
        #             which_plugin = data['topology'][i]
        #             env_index = cost_dict[(next_node -1) % num_env]
        #             total_time = total_time + runtime_dict[which_plugin][env_index]
        #             total_cost = total_cost + cost_dict[env_index]
        #             # if v == 0:
        #             #     total_time = total_time + runtime_dict[which_plugin][cost_dict[next_node % num_env]]
        #             # else:
        #             #     total_time = total_time + runtime_dict[which_plugin][cost_dict[int(next_node-this_node-num_env)]]

        #             # print(path)
        #         # print(path[:-1])
        #         # print('total time = ', total_time)
        #         # print('total cost =', total_cost)
        #         ### replace the current best path if it doesn't go over budget and any of the following is true
        #         ### 1. there's no best path yet
        #         ### 2. current path has better time
        #         ### 3. current path has same time but with lower cost
        #         if total_cost <= budget:
        #             if total_time < best_path_time or best_path_time == -1:
        #                 best_path_time = total_time
        #                 best_path_cost = total_cost
        #                 best_path = path
        #             if total_time == best_path_time and total_cost< best_path_cost:
        #                 best_path_time = total_time
        #                 best_path_cost = total_cost
        #                 best_path = path



        #     # print("best path:", best_path)
        #     ### chaging from path to which env
        #     env_path = []
        #     for i,v in enumerate(best_path[:-2]):
        #         next_node = best_path[i+1]
        #         env_index = int(cost_dict[(next_node -1) % num_env])
        #         env_name = list(compute_resources)[env_index]['name']
        #         env_path.append(env_name)

        #     return_dict = {}
        #     return_dict['status'] = 'OK'
        #     #return_dict['env selection'] = env_path
        #     #print("plugin sequence: ", [plugin['plugin_name'] for plugin in data['plugin_list']])
        #     match_list = []
        #     for index,plugin in enumerate(data['plugin_list']):
        #         temp_dict = {}
        #         temp_dict[plugin['plugin_name']] = env_path[index]
        #         match_list.append(temp_dict)
        #     return_dict['match_result'] = match_list
        #     ### 3.2 traverse the rest of the path,
        #     ###         if during the travsersal the cost exceed budget, skip it
        #     ###         if during the travsersal the expected runtime exceed best path expected runtime, skip it
        #     ###         when travsersal complete, compare the expected runtime, set path with lower runtime as best path
        #     ### 4. calculate the rest of the path
        #     ### 5. output the path it takes

        #     return return_dict


    def list_all_pipelines(self):
        return_dict = {}
        ### get pipeline json object from database
        res = self._s.get(self.addr + 'pipelines')
        res.raise_for_status()
        data = res.json()
        pipelines = data['results']
        pipeline_names = {}
        for pipeline in pipelines:
            pipeline_name = pipeline['name']
            pipeline_names[str(pipeline_name)] = pipeline
        return pipeline_names


    def pipeline_name_to_id(self, pipeline_name: str):
        res = self._s.get(self.addr + 'pipelines')
        res.raise_for_status()
        data = res.json()
        pipelines = data['results']
        for pipeline in pipelines:
            if pipeline_name == pipeline['name']:
                return pipeline['id']
        print("Cannot not convert pipeline_name to id")
        exit(-1)


    def get_rec_compute_env(self, plugin_name, passed_env_list, budget):
        """
            get plugin_name

        """
        ### TO DO
        ### get all compute env cost
        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        env_data = res.json()
        cost_dict = {}
        compute_resources = env_data['results']

        ### get plugin details
        plugin_details = self.get_plugin_details(plugin_name=plugin_name)
        compute_addr = plugin_details[plugin_name]['compute_resources']
        min_cpu_limit = plugin_details[plugin_name]['min_cpu_limit']
        min_gpu_limit = plugin_details[plugin_name]['min_gpu_limit']
        min_memory_limit = plugin_details[plugin_name]['min_memory_limit']
        min_number_of_workers = plugin_details[plugin_name]['min_number_of_workers']

        best_path_time = -1
        for i, env in enumerate(compute_resources):
            if env['name'] not in ['auto_free', 'auto_best'] and env['name'] in passed_env_list:
                expected_runtime = 1000  # this should be changed to input size
                ### need to change how we calculate expected_runtime
                if min_gpu_limit == 0:
                    expected_runtime = expected_runtime / (env['cpus']*env['cpu_clock_speed_ghz'] + 0.2 * ((env['memory']) / min_memory_limit) + 0.001)
                else:
                    expected_runtime = expected_runtime / (env['cpus']*env['cpu_clock_speed_ghz'] + 0.2 * ((env['memory']) / min_memory_limit) + 0.5 * env['gpus']   + 0.001)
                    
                ### get best time
                if (expected_runtime < best_path_time or best_path_time == -1) and env['cost'] <= budget:
                    best_path_time = expected_runtime
                    best_env = env['name']

        return best_env
