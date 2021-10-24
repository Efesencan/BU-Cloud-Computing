"""
Session token storage mechanisms.

If available, the desktop keyring is used. Else a session token
(not the account password) will be stored in plaintext.
"""
import abc
import json
from abc import ABC
from typing import Optional, Callable
import typer
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

use_keyring = True
try:
    import keyring
    logger.info('Using keyring')
except ModuleNotFoundError:
    use_keyring = False
    logger.info('Using plaintext')


class NotLoggedInError(Exception):
    pass


class AbstractSecretStore(ABC):
    """
    A key-value data structure which hopefully stores its values securely.
    It can read and write to the application's settings, though saving of those
    settings is not its responsibility.

    The application's settings are not necessarily stored securely. Instead, it
    is the responsibility of this AbstractSecretStore to store secrets securely
    somewhere else (optionally using the application's settings as pointers).
    """

    def __init__(self, context: dict):
        """
        :param context: application settings which are expected to be saved
                        after the invocation of this object's methods
        """
        self.context = context

    @abc.abstractmethod
    def get(self, address: str) -> str:
        ...

    @abc.abstractmethod
    def set(self, address: str, token: str):
        ...

    @abc.abstractmethod
    def clear(self, address: str):
        ...


class KeyringSecretStore(AbstractSecretStore):
    """
    Secure token storage using the host desktop environment's login keyring.
    """

    __SPACE = 'org.chrisproject.caw'

    def get(self, address: str) -> str:
        token = keyring.get_password(self.__SPACE, address)
        if not token:
            raise NotLoggedInError()
        return token

    def set(self, address: str, token: str):
        keyring.set_password(self.__SPACE, address, token)

    def clear(self, address: str):
        keyring.delete_password(self.__SPACE, address)


class FallbackSecretStore(AbstractSecretStore):
    """
    Insecure token storage in plaintext.
    This implementation should only be used when the keyring is not available.
    """
    def __init__(self, context: dict):
        super().__init__(context)
        if 'secrets' not in context:
            context['secrets'] = {}

    def get(self, address: str) -> str:
        if address not in self.context['secrets']:
            raise NotLoggedInError()
        return self.context['secrets'][address]

    def set(self, address: str, token: str):
        self.context['secrets'][address] = token

    def clear(self, address: str):
        del self.context['secrets'][address]


class LoginManager:
    """
    A wrapper around an AbstractSecretStore which handles saving of configurations.

    The configuration file is saved in ~/.config/caw after each method call.
    """

    def __init__(self, PreferredSecretStore: Optional[Callable[[dict], AbstractSecretStore]] =
                 KeyringSecretStore if use_keyring else FallbackSecretStore,
                 config_file: Optional[Path] = Path(typer.get_app_dir('caw')) / 'login.json'):
        # new empty configuration on first run
        if not config_file.exists():
            appdir = Path(typer.get_app_dir('caw'))
            if config_file.parent == appdir:
                appdir.mkdir(parents=True)
            config_file.write_text('{}')

        self.__savefile = config_file
        with self.__savefile.open('r') as f:
            self.__store = PreferredSecretStore(json.load(f))

    def get_default_address(self) -> Optional[str]:
        if 'defaultAddress' not in self.__store.context:
            return None
        return self.__store.context['defaultAddress']

    def __default_address(self, address: Optional[str] = None):
        """
        Get the default address from the configuration if the address was not given.
        :param address: CUBE address
        :return: CUBE address
        """
        if address:
            return address
        default_address = self.get_default_address()
        if not default_address:
            raise NotLoggedInError('Default CUBE address has not yet been set.')
        return default_address

    def __write_config(self):
        """
        Save login configuration to disk.
        """
        with self.__savefile.open('w') as f:
            json.dump(self.__store.context, f)

    def get(self, address: Optional[str] = None):
        address = self.__default_address(address)
        return self.__store.get(address)

    def logout(self, address: Optional[str] = None):
        """
        Remove secret from storage. If the address is the default address, then remove the default address as well.
        :param address: CUBE address
        """
        if not address:
            address = self.__default_address(address)
            del self.__store.context['defaultAddress']

        self.__store.clear(address)
        self.__write_config()

    def login(self, address: str, token: str):
        self.__store.set(address, token)
        self.__store.context['defaultAddress'] = address
        self.__write_config()

        if not use_keyring and isinstance(self.__store, FallbackSecretStore):
            typer.secho(f'Login token was saved as plaintext in the file ', dim=True, err=True)
            typer.secho(str(self.__savefile), dim=True, err=True)
            typer.secho('For safer identification storage, please run: '
                        '\n\n\tcaw logout'
                        '\n\tpip install keyring'
                        f'\n\tcaw login --address {address}\n',  dim=True, err=True)
