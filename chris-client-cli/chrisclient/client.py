from os import path
import requests
from typing import Optional, Set, Union, Dict
import json

from .models import PluginInstance, Plugin, Pipeline, UploadedFiles, Feed, ComputeResource
### for debugging
import networkx as nx
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

    def get_plugin_details(self, plugin_id = None, plugin_name = None):
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
        #print(json.dumps(dict_plugin, sort_keys=True, indent=4))
        return dict_plugin
    
    def check_plugin_compute_env(self, plugin_name):
        plugin_details = self.get_plugin_details(plugin_name = plugin_name)
        compute_addr = plugin_details[plugin_name]['compute_resources']
        min_cpu_limit = plugin_details[plugin_name]['min_cpu_limit']
        min_gpu_limit = plugin_details[plugin_name]['min_gpu_limit']
        min_memory_limit = plugin_details[plugin_name]['min_memory_limit']
        min_number_of_workers = plugin_details[plugin_name]['min_number_of_workers']

        res = self._s.get(self.addr_compute_resources)
        res.raise_for_status()
        data = res.json()
        #print(json.dumps(data, sort_keys=True, indent=4))
        compute_resources = data['results']
        match_dict = {}
        match_list = []
        match_dict['plugin_name'] = plugin_name
        for resource in compute_resources:
            cmp_cpu = resource['cpus']
            cmp_gpu = resource['gpus']
            cmp_cost = resource['cost']
            cmp_mem = resource['memory']
            cmp_worker = resource['workers']
            if cmp_cpu >= min_cpu_limit and cmp_gpu >= min_gpu_limit and cmp_mem >= min_memory_limit and cmp_worker >= min_number_of_workers:
                match_list.append({resource['name']: {'fit': True}})
            else:
                match_list.append({resource['name']: {'fit': False}})
        match_dict['matching'] = match_list

        # print(json.dumps(match_dict, sort_keys=True, indent=4))
        return match_dict

    def get_plugin_from_pipeline(self, pipeline_id: int):
        return_dict = {}
        ### get pipeline json object from database
        res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
        res.raise_for_status()
        data = res.json()
        
        ### get plugins topography from database
        res_topo = self._s.get(data['plugin_pipings'])
        res_topo.raise_for_status()
        data_topo = res_topo.json()
        ### networkx graph object
        G = nx.DiGraph()
        link_list = data_topo['results']
        identity_dict = {} ### keep track of which node_id is corresponding to which plugin id
        for link in link_list:
            identity_dict[link['id']] = link['plugin_id']
            if 'previous_id' in link:
                previous_label = link['previous_id']
                this_label = link['id']
                G.add_edge(previous_label, this_label)
        topolopy = list(nx.topological_sort(G)) ### list of node_id dictating which node come first
        plugin_id_topo = [identity_dict[k] for k in topolopy]
        

        ### get list of plugins associated with that pipeline json object from database
        res = self._s.get(data['plugins'])
        res.raise_for_status()
        data = res.json()
        
        plugin_list = data['results']
        # pp = pprint.PrettyPrinter(indent=4)
        # pp.pprint(data)
        
        ### extract information from each plugins
        return_dict['status'] = 'OK'
        return_dict['plugin_list'] = []
        for plugin in plugin_list:
            # print(plugin)
            current_plugin = {}
            current_plugin['plugin_id'] = plugin['id']
            current_plugin['plugin_name'] = plugin['name']
            return_dict['plugin_list'].append(current_plugin)
        return_dict['topology_nodeid'] = topolopy
        return_dict['topology'] = plugin_id_topo
        return return_dict
    ###     
    def match_pipeline(self, pipeline_id: int, budget: int = 0):
        '''
        overview: 
            takes in pipeline_id, budget and compute how to assign each plug-in to acheive lowest runtime while staying under budget
        input:  
            pipeline_id = id of the pipeline to be processed\n
            budget = amount of availiable cost that constrain the compute environment assignment
        output: a dictionary with list of compute environment assignment
        '''


        return_dict = {}

        ### 1. get all plug-in id from the given pipeline
        # payload = {
        #     'id': pipeline_id
        # }
        
        ### get pipeline json object from database
        res = self._s.get(self.addr + 'pipelines/' + str(pipeline_id))
        res.raise_for_status()
        data = res.json()
        ### get list of plugins associated with that pipeline json object from database
        res = self._s.get(data['plugins'])
        res.raise_for_status()
        data = res.json()
        plugin_list = data['results']
        # print(data)
        ### extract information from each plugins
        for plugin in plugin_list:
            # print(plugin)
            plugin_id = plugin['id']
            plugin_name = plugin['name']

        
        # ### 2. for each plug-in get the expected runtime and cost
        # for plugin_id in plugin_list:
        #     plugin_details = self.get_plugin_details(plugin_id= plugin_id)
        #     compute_addr = plugin_details[plugin_id]['compute_resources']
        #     min_cpu_limit = plugin_details[plugin_id]['min_cpu_limit']
        ### 3. construct a network where node = current plug-in, edge = the environment to take, weight = expected runtime
        ### 3.1 traverse the 1st path, record its total cost, set it as best path
        ### 3.2 traverse the rest of the path, 
        ###         if during the travsersal the cost exceed budget, skip it 
        ###         if during the travsersal the expected runtime exceed best path expected runtime, skip it 
        ###         when travsersal complete, compare the expected runtime, set path with lower runtime as best path
        ### 4. calculate the rest of the path
        ### 5. output the path it takes

        return return_dict






