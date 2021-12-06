import os
import requests
from datetime import datetime
from .util import collection_helper, PaginationNotImplementedException
from typing import Optional, Set, Union, Iterator
from collections.abc import Iterable
from pathlib import Path
from abc import ABC
from queue import Queue
import logging

PAGINATION_LIMIT = os.getenv('CAW_PAGINATION_LIMIT', 64)


class ConnectedResource(ABC):
    """
    An object returned from the CUBE API which can make further requests to the API.
    """

    def __init__(self, url: str, session: requests.Session):
        self.url = url
        self._s = session

    def __hash__(self):
        return hash(self.url)


class Feed(ConnectedResource):
    def __init__(self, feed_url, session: requests.Session):
        super().__init__(feed_url, session)

        res = self._s.get(feed_url).json()
        self._note_url = res['note']

    def set_name(self, name):
        payload = collection_helper({'name': name})
        res = self._s.put(self.url, json=payload)
        res.raise_for_status()
        return res.json()

    def set_description(self, description):
        payload = collection_helper({
            'title': 'Description',
            'content': description
        })
        res = self._s.put(self._note_url, json=payload)
        res.raise_for_status()
        return res.json()


class PluginInstance(ConnectedResource):
    def __init__(self, url: str, id: int, title: str, feed: str, session: requests.Session, **kwargs):
        super().__init__(url, session)
        self.id = id
        self.title = title
        self.feed = feed

    def get_feed(self):
        return Feed(feed_url=self.feed, session=self._s)

    def append_pipeline(self, pipeline: 'Pipeline'):
        """
        Run a pipeline as a generator of plugin instances. Every ``next()`` creates a plugin instance.
        :param pipeline: pipeline to run
        """

        instances_map = {
            'None': self.id
        }
        """
        Maps Piping IDs to newly created PluginInstance IDs.
        """

        for p in pipeline:
            params = {
                'previous_id': instances_map[str(p.previous_id)]
            }
            params.update(p.default_parameters)
            next_instance = p.plugin.create_instance(params)
            yield next_instance
            instances_map[str(p.id)] = next_instance.id


class Plugin(ConnectedResource):
    def __init__(self, id: int, name: str, version: str,
                 instances: str, url: str, session: requests.Session, **kwargs):
        super().__init__(url, session)
        self.id = id
        self.name = name
        self.version = version
        self.instances = instances

    def create_instance(self, params: dict = None) -> PluginInstance:
        payload = collection_helper(params)

        res = self._s.post(self.instances, json=payload)
        res.raise_for_status()
        return PluginInstance(**res.json(), session=self._s)


class Piping(Iterable):
    """
    A Piping is the information about a plugin's membership of a pipeline.
    It is a node of a directed acyclic graph representation of a pipeline.
    Edges are bidirectional. A Piping knows its parent and its children.
    """

    def __init__(self, id: int, pipeline: str, pipeline_id: int, plugin: str, plugin_id: int, url: str,
                 default_parameters: dict, session: requests.Session, previous: Optional[str],
                 previous_id: Optional[int] = None):
        self.id = id
        self.pipeline = pipeline
        self.pipeline_id = pipeline_id
        self.plugin_id = plugin_id
        self.url = url
        self.previous = previous
        self.previous_id = previous_id
        self.children: Set['Piping'] = set()
        """Graph edges to children"""
        self.parent: Optional['Piping'] = None
        """Graph edge to parent"""
        self.default_parameters = default_parameters

        res = session.get(plugin)
        res.raise_for_status()
        self.plugin = Plugin(**res.json(), session=session)

    def __hash__(self):
        return hash((self.id, self.pipeline_id))

    def add_child(self, child: 'Piping'):
        self.children.add(child)

    def _to_queue(self) -> Queue:
        """
        Convert the tree to a queue where the root is first, and dependency plugins appear
        before the plugins which depend on them.
        :return: queue for a breadth-first traversal over the graph
        """
        q = Queue()
        self._add_all_to_queue(q, self)
        return q

    @classmethod
    def _add_all_to_queue(cls, q: Queue, p: 'Piping'):
        q.put(p)
        for c in p.children:
            cls._add_all_to_queue(q, c)

    def __iter__(self) -> Iterator['Piping']:
        """
        Breadth-first graph traversal.
        """
        q = self._to_queue()
        while not q.empty():
            yield q.get_nowait()
            q.task_done()


class PipelineAssemblyException(Exception):
    """
    Pipeline JSON representation cannot be reassembled as a Piping DAG.
    """
    pass


class PipelineHasMultipleRootsException(PipelineAssemblyException):
    """
    Multiple pipings with 'previous': null were found in the pipeline JSON representation.
    """
    pass


class PipelineRootNotFoundException(PipelineAssemblyException):
    """
    No piping found in the pipelines JSON representation with 'previous': null.
    """
    pass


class ComputeResource(ConnectedResource):
    def __init__(self, name: str, compute_url: str, description: str, url: str, session: requests.Session, **kwargs):
        super().__init__(url, session)
        self.name = name
        self.compute_url = compute_url
        self.description = description


class Pipeline(ConnectedResource):
    def __init__(self, authors: str, description: str, name: str, plugin_pipings: str, default_parameters: str,
                 plugins: str, url: str, session: requests.Session, **kwargs):
        super().__init__(url, session)
        self.authors = authors
        self.description = description
        self.name = name
        self.plugin_pipings = plugin_pipings
        self.default_parameters = default_parameters
        self.plugins = plugins
        self.pipings = self._do_get(self.plugin_pipings)

    def _do_get(self, url):
        res = self._s.get(url, params={'limit': PAGINATION_LIMIT, 'offset': 0})
        res.raise_for_status()
        data = res.json()
        if data['next']:
            raise PaginationNotImplementedException()
        return data['results']

    def get_default_parameters(self):
        return self._do_get(self.default_parameters)

    def assemble(self) -> Piping:
        """
        Convert the responses from CUBE to a DAG with parent --> child relationships
        (whereas CUBE's response represents a pipeline via child --> parent relationships
        through the previous key) and couples parameter info with plugin info.
        :return: DAG
        """
        # collect all default parameters
        assembled_params = {}
        for param_info in self.get_default_parameters():
            i = param_info['plugin_piping_id']
            if i not in assembled_params:
                assembled_params[i] = {}
            assembled_params[i][param_info['param_name']] = param_info['value']

        pipings_map = {}
        root: Optional[Piping] = None

        # create DAG nodes
        for piping_info in self.pipings:
            i = piping_info['id']
            if i in assembled_params:
                params = assembled_params[i]
            else:
                params = {}
            piping = Piping(**piping_info, default_parameters=params, session=self._s)
            pipings_map[i] = piping

            if not piping.previous:
                if root:
                    raise PipelineHasMultipleRootsException()
                root = piping
        if not root:
            raise PipelineRootNotFoundException()

        # create bidirectional DAG edges
        for _, piping in pipings_map.items():
            i = piping.previous_id
            if not i:
                continue
            pipings_map[i].add_child(piping)
            piping.parent = pipings_map[i]

        return root

    def __len__(self) -> int:
        """
        :return: number of pipings
        """
        return len(self.pipings)

    def __iter__(self):
        return iter(self.assemble())


class UploadedFile(ConnectedResource):
    """
    Represents a file resource in CUBE.

    TODO: rename to RegisteredFile
    """

    def __init__(self, creation_date: str, file_resource: str, fname: str, fsize: int, id: int,
                 url: str, session: requests.Session,
                 owner: Optional[str] = None,
                 feed_id: Optional[int] = None, plugin_inst: Optional[str] = None,
                 plugin_inst_id: Optional[int] = None,

                 PatientID: Optional[str] = None,
                 PatientName: Optional[str] = None,
                 PatientBirthDate: Optional[str] = None,
                 PatientAge: Optional[float] = None,  # float or int?
                 PatientSex: Optional[str] = None,
                 StudyDate: Optional[str] = None,
                 Modality: Optional[str] = None,
                 ProtocolName: Optional[str] = None,
                 StudyInstanceUID: Optional[str] = None,
                 StudyDescription: Optional[str] = None,
                 SeriesInstanceUID: Optional[str] = None,
                 SeriesDescription: Optional[str] = None,
                 pacs_identifier: Optional[str] = None):
        super().__init__(url, session)
        self.creation_date = datetime.fromisoformat(creation_date)
        self.file_resource = file_resource
        self.fname = fname
        self.fsize = fsize
        self.id = id
        self.ownder = owner
        self.feed_id = feed_id
        self.plugin_inst = plugin_inst
        self.plugin_inst_id = plugin_inst_id

        self.PatientID = PatientID
        self.PatientName = PatientName
        self.PatientBirthDate = PatientBirthDate
        self.PatientAge: Optional[float] = PatientAge
        self.PatientSex = PatientSex
        self.StudyDate = StudyDate
        self.Modality = Modality
        self.ProtocolName = ProtocolName
        self.StudyInstanceUID = StudyInstanceUID
        self.StudyDescription = StudyDescription
        self.SeriesInstanceUID = SeriesInstanceUID
        self.SeriesDescription = SeriesDescription
        self.pacs_identifier = pacs_identifier

    def download(self, destination: Union[Path, str], chunk_size=8192):
        with self._s.get(self.file_resource, stream=True, headers={'Accept': None}) as r:
            r.raise_for_status()
            with open(destination, 'wb') as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)


class InvalidFilesResourceUrlException(Exception):
    pass


class UploadedFiles(ConnectedResource, Iterable):
    """
    Lazy iterable over paginated response.
    """
    __logger = logging.getLogger('UploadedFiles')

    def __init__(self, url: str, session: requests.Session):
        super().__init__(url, session)
        if 'limit=' not in self.url:
            self.url += f"{'&' if '?' in self.url else '?'}limit={PAGINATION_LIMIT}"

        try:
            self._initial_data = self._do_get(self.url)
        except requests.exceptions.HTTPError as e:
            raise InvalidFilesResourceUrlException(f'{e.response.status_code} error getting {self.url}')
        # check given URL is a files collection resource
        if 'count' not in self._initial_data:
            raise InvalidFilesResourceUrlException(f'{self.url} does not look like a files collection resource.')
        if self._initial_data['count'] > 0:
            try:
                UploadedFile(session=self._s, **self._initial_data['results'][0])
            except KeyError:
                raise InvalidFilesResourceUrlException(f'{self.url} is not a files collection resource.')

    def __iter__(self) -> Iterator[UploadedFile]:
        data = self._initial_data  # first page
        if data['previous'] is not None:
            self.__logger.warning('%s is not the first page.', self.url)

        while data['next']:
            for fdata in data['results']:
                yield UploadedFile(**fdata, session=self._s)
            self.__logger.debug('next page: %s', data['next'])
            data = self._do_get(data['next'])  # next page
        for fdata in data['results']:  # last page
            yield UploadedFile(**fdata, session=self._s)

    def __len__(self):
        return self._initial_data['count']

    def _do_get(self, url):
        self.__logger.info('getting %s', url)
        res = self._s.get(url)
        res.raise_for_status()
        return res.json()
