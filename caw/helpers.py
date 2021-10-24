"""
This file eases usage of the Python chris.client and Typer.
"""
import os
import typer

from chris.models import Pipeline, PluginInstance
from chris.client import ChrisClient, ChrisIncorrectLoginError, PipelineNotFoundError
from caw.globals import DEFAULT_ADDRESS, DEFAULT_PASSWORD
from caw.login import LoginManager, NotLoggedInError

import logging
logger = logging.getLogger(__name__)


def run_pipeline(chris_pipeline: Pipeline, plugin_instance: PluginInstance):
    """
    Helper to execute a pipeline with a progress bar.
    """
    with typer.progressbar(plugin_instance.append_pipeline(chris_pipeline),
                           length=len(chris_pipeline.pipings), label='Scheduling pipeline') as proto_pipeline:
        for _ in proto_pipeline:
            pass


class FriendlyClient(ChrisClient):
    """
    A ``ChrisClient`` which shows (less helpful) error messages instead of exceptions.
    """
    def get_pipeline(self, name: str) -> Pipeline:
        try:
            return super().get_pipeline(name)
        except PipelineNotFoundError:
            typer.secho(f'Pipeline not found: "{name}"', fg=typer.colors.RED, err=True)
            raise typer.Abort()


class ClientPrecursor:
    """
    A workaround so that the ChrisClient object's constructor, which attempts to use the login
    credentials, is called by the subcommand instead of the main callback.

    This is necessary to support the ``caw login`` subcommand.
    """
    def __init__(self, login_manager: LoginManager):
        self.login_manager = login_manager

        self.address = None
        self.username = None
        self.password = None
        self.token = None

    def __call__(self) -> ChrisClient:
        """
        Authenticate with ChRIS and construct the client object.

        Login strategy:
        1. First, use given credentials.
        2. If credentials not specified, use saved login.

        :return: client object
        """
        if not self.address:
            raise ValueError('Must specify CUBE address.')

        # check if previously logged in
        if self.address == DEFAULT_ADDRESS:
            saved_address = self.login_manager.get_default_address()
            if saved_address:
                self.address = saved_address
        logger.debug('CUBE address: %s', self.address)

        if self.password == DEFAULT_PASSWORD:  # assume password not specified
            try:
                self.token = self.login_manager.get(self.address)
            except NotLoggedInError:  # password not specified and not previously logged in
                if 'CHRIS_TESTING' not in os.environ:
                    typer.secho('Using defaults (set CHRIS_TESTING=y to suppress this message): '
                                f'{self.address}  {self.username}:{self.password}', dim=True, err=True)

        # If previously logged in, use token to authenticate.
        # Otherwise, use username and password combo (which may or may not be be the default chris:chris1234).
        try:
            if self.token:
                logger.debug('HTTP token: "%s"', self.token)
                return FriendlyClient(self.address, token=self.token)
            else:
                return FriendlyClient(self.address, username=self.username, password=self.password)
        except ChrisIncorrectLoginError as e:
            typer.secho(e.args[0], err=True)
            raise typer.Abort()
        except Exception:
            typer.secho('Connection error\n'
                        f'address:  {self.address}\n'
                        f'username: {self.username}', fg=typer.colors.RED, err=True)
            raise typer.Abort()
