'''
Created on Nov 30, 2021

@author: carlos.anguiano
'''

from shot_grid_sub_2_dailies.sub2d_api import Sub2DAPI, Shotgun
import unittest


class TestSub2DAPI(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)

        self._creds = {'url': 'https://nocompanyrnd.shotgrid.autodesk.com/',
                       'user': 'TechArtUserLib',
                       'password': 'eenlolpuj-Ypjuoxhpr8vwjbt',
                       'is_user': False}

        Sub2DAPI.set_cache_settings(self._creds['url'],
                                    self._creds['user'],
                                    self._creds['password'])

        self._api = Sub2DAPI()

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        Sub2DAPI.clear_cache_settings()

    def test_set_cache_settings(self):
        # NOTE: use bad password key
        with self.assertRaises(RuntimeError):
            Sub2DAPI.set_cache_settings(self._creds['url'],
                                        self._creds['user'],
                                        'fart bad key sad face :(')
        # NOTE: use good creds
        Sub2DAPI.set_cache_settings(self._creds['url'],
                                    self._creds['user'],
                                    self._creds['password'])

    def test_get_settings(self):
        Sub2DAPI.clear_cache_settings()
        settings = Sub2DAPI._get_cached_settings()
        self.assertEqual(settings, None)

        Sub2DAPI.set_cache_settings(self._creds['url'],
                                    self._creds['user'],
                                    self._creds['password'])

        settings = Sub2DAPI._get_cached_settings()
        self.assertDictEqual(self._creds, settings)

    def test_sg_property(self):
        Sub2DAPI.clear_cache_settings()
        with self.assertRaises(RuntimeError):
            print(self._api.sg)

        Sub2DAPI.set_cache_settings(self._creds['url'],
                                    self._creds['user'],
                                    self._creds['password'])

        self.assertTrue(isinstance(self._api.sg, Shotgun))

    def test_get_projects(self):
        Sub2DAPI.set_cache_settings(self._creds['url'],
                                    self._creds['user'],
                                    self._creds['password'])

        projects = self._api.get_projects()
        self.assertTrue(len(projects) > 0)

        val_types = [proj['type']
                     for proj in projects if proj['type'] == 'Project']

        self.assertEqual(len(val_types), len(projects))

    def test_get_assets(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        assets = self._api.get_assets(prjs[0])
        self.assertTrue(len(assets) > 0)

        val_types = [asset['type']
                     for asset in assets if asset['type'] == 'Asset']

        self.assertEqual(len(val_types), len(assets))

    def test_get_sequences(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        sequences = self._api.get_sequences(prjs[0])
        self.assertTrue(len(sequences) > 0)

        val_types = [sequence['type']
                     for sequence in sequences if sequence['type'] == 'Sequence']

        self.assertEqual(len(val_types), len(sequences))

    def test_get_shots(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        seqs = self._api.get_sequences(prjs[0], name='bunny_070')
        shots = self._api.get_shots(seqs[0])
        self.assertTrue(len(shots) > 0)

        val_types = [shot['type']
                     for shot in shots if shot['type'] == 'Shot']

        self.assertEqual(len(val_types), len(shots))

    def test_get_tasks(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        seqs = self._api.get_sequences(prjs[0], name='bunny_070')
        shots = self._api.get_shots(seqs[0])
        self.assertTrue(len(shots) > 0)

        tasks = self._api.get_tasks(shots[0])
        self.assertTrue(len(tasks) > 0)

        val_types = [task['cached_display_name'] for task in tasks if task['type'] == 'Task']

        self.assertEqual(len(val_types), len(tasks))

    def test_get_task_versions(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        seqs = self._api.get_sequences(prjs[0], name='bunny_070')
        shots = self._api.get_shots(seqs[0])

        tasks = self._api.get_tasks(shots[0])
        versions = self._api.get_task_version(tasks[0])
        self.assertTrue(len(versions) > 0)
        val_types = [ver['code'] for ver in versions if ver['type'] == 'Version']
        self.assertEqual(len(val_types), len(versions))

    def test_allocate_version_name(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        seqs = self._api.get_sequences(prjs[0], name='bunny_070')
        shots = self._api.get_shots(seqs[0])
        tasks = self._api.get_tasks(shots[0])

        u_ver_name = self._api.gen_unique_version_name(tasks[0], 'temp_sg_upload_media')

        self.assertEqual(u_ver_name, 'temp_sg_upload_media_v0011')

    def test_make_version_for_task(self):
        prjs = self._api.get_projects(name='Demo: Animation')
        seqs = self._api.get_sequences(prjs[0], name='bunny_070')
        shots = self._api.get_shots(seqs[0])
        tasks = self._api.get_tasks(shots[0])

        new_ver = self._api.make_version_for_task(tasks[0],
                                                  'unnit_test_version',
                                                  'this version was made by a unit test')

        self.assertEqual(new_ver['type'], 'Version')
        self.assertEqual(new_ver['code'], 'unnit_test_version_v0001')
        self.assertEqual(new_ver['sg_task']['id'], tasks[0]['id'])

        # NOTE: making sure the version up is taking place
        new_ver2 = self._api.make_version_for_task(tasks[0],
                                                   'unnit_test_version',
                                                   'this version was made by a unit test')
        self.assertEqual(new_ver2['code'], 'unnit_test_version_v0002')

        self._api.sg.delete('Version', new_ver['id'])  # clean up
        self._api.sg.delete('Version', new_ver2['id'])  # clean up


if __name__ == '__main__':
    unittest.main()
