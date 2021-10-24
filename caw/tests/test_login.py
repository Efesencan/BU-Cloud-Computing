import unittest
from unittest import TestCase, mock
from pathlib import Path
from caw.login import AbstractSecretStore, KeyringSecretStore, FallbackSecretStore,\
    NotLoggedInError, LoginManager, use_keyring
from tempfile import NamedTemporaryFile


class TestSecretStore(TestCase):
    def can_save_clear(self, store: AbstractSecretStore):
        store.set('http://localhost:8910/api/v1/', 'abcdefg')
        stored = store.get('http://localhost:8910/api/v1/')
        self.assertEqual(stored, 'abcdefg', msg='Stored secret does not match what was originally set.')
        store.clear('http://localhost:8910/api/v1/')
        with self.assertRaises(NotLoggedInError, msg='Secret was not removed.'):
            store.get('http://localhost:8910/api/v1/')

    @unittest.skipUnless(use_keyring, 'keyring not supported')
    def test_keyring(self):
        self.can_save_clear(KeyringSecretStore({}))

    def test_plaintext(self):
        self.can_save_clear(FallbackSecretStore({}))


class TestLoginManager(TestCase):
    def test_default_address(self):
        store = FallbackSecretStore({})

        with NamedTemporaryFile(suffix='.json', delete=True) as savefile:
            pass

        lm = LoginManager(lambda _: store, Path(savefile.name))

        store.set = mock.Mock()
        lm.login('https://example.com/api/v1/', 'berry')
        store.set.assert_called_once_with('https://example.com/api/v1/', 'berry')
        self.assertIn('defaultAddress', store.context,
                      msg='Login manager did not set the CUBE address as default.')
        self.assertEqual(store.context['defaultAddress'], 'https://example.com/api/v1/',
                         msg='Default address is incorrect.')

        store.get = mock.Mock(return_value='berry')
        self.assertEqual(lm.get(), 'berry', msg='Retrieved password for default CUBE address is incorrect.')

        store.clear = mock.Mock()
        lm.logout()
        store.clear.assert_called_once_with('https://example.com/api/v1/')
        self.assertNotIn('defaultAddress', store.context,
                         msg='Default address not removed after logout.')
