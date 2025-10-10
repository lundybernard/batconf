from unittest import TestCase

from os import environ
from concurrent.futures import ThreadPoolExecutor

from project.conf import get_config
from project.submodule.client import MyClient


class ThreadSafetyTests(TestCase):
    """Ensure thread safety when using python with free-threading
    Supported behavior:
        Accessing values on the Configuration object from many threads is safe
    Unsupported behavior:
        Setting attributes on a shared config object is NOT safe,
        or recommended.
    """

    def setUp(t):
        environ['PROJECT_SUBMODULE_CLIENT_KEY2'] = 'override_value'

    def tearDown(t):
        del environ['PROJECT_SUBMODULE_CLIENT_KEY2']

    def test_config_class(t):
        cfg = get_config()

        def worker(thread_id):
            # hammer the cfg object
            for i in range(10):
                # read values off of the Configuration object many times
                t.assertEqual(cfg.submodule.client.key2, 'override_value')
                t.assertEqual(
                    cfg.clients.clientA.key1,
                    'config.ini: clientA.key1',
                )
                t.assertEqual(
                    cfg.clients.clientB.key1,
                    'config.ini: clientB.key1',
                )

                # create a client in each thread, multiple times.
                client = MyClient.from_config(cfg.submodule.client)
                client.key1 = thread_id
                # client attribute values do not clobber each other
                t.assertEqual(client.key1, thread_id)

            return client.fetch_data()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(worker, i)  #
                for i in range(20)  #
            ]
            for future in futures:
                ret = future.result()
                print(ret)
