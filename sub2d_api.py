'''
Created on Nov 30, 2021

@author: carlos.anguiano
'''
import json
import os
from shot_grid_sub_2_dailies.ffmpeg_helper import FFMpegHelper
from tempfile import gettempdir

from shotgun_api3 import Shotgun
from shotgun_api3.shotgun import AuthenticationFault, ShotgunError


class Sub2DAPI(object):
    _sg_api = None
    media_formats = {'.jpg': 'image',
                     '.exr': 'image'}

    def __init__(self):
        self._ffmpeg = FFMpegHelper()

    @property
    def sg(self):
        if not self._sg_api:
            self._sg_api = self._init_shotgun()

        return self._sg_api

    @classmethod
    def _init_shotgun(cls, settings=None):
        settings = settings or cls._get_cached_settings()
        if not settings:
            raise RuntimeError(
                'There are no Shotgrid credentials stored on the system')

        # NOTE: script based authentications
        if not settings['is_user']:
            sg = Shotgun(settings['url'],
                         script_name=settings['user'],
                         api_key=settings['password'])
        # NOTE: user based authentication
        else:

            sg = Shotgun(settings['url'],
                         login=settings['user'],
                         password=settings['password'])

        try:
            prjs = sg.find('Project', [])
        except AuthenticationFault as msg:
            raise RuntimeError('Could not log in with the given creds\n%s' % str(msg))

        return sg

    @staticmethod
    def _get_settings_file_path():
        appdatapath = '%APPDATA%\ZeniMaxGlobalTechArtApps\Shotgri_Sub2D\setting.json'
        return os.path.expandvars(appdatapath)

    @classmethod
    def _get_cached_settings(cls):
        '''

        '''
        setting_json = cls._get_settings_file_path()
        if not os.path.isfile(setting_json):
            return None

        with open(setting_json, 'r') as strm:
            return json.loads(strm.read())

    @classmethod
    def set_cache_settings(cls, url, user, password, is_user=False):
        '''
        store credentials in user machine

        :param url:
        :param user:
        :param password:
        '''
        # NOTE: verify creds before storing them
        setting_dic = {'url': url,
                       'user': user,
                       'password': password,
                       'is_user': is_user}

        # NOTE: validate the credentials
        cls._init_shotgun(settings=setting_dic)

        setting_json = cls._get_settings_file_path()

        rdir = os.path.dirname(setting_json)

        if not os.path.isdir(rdir):
            os.makedirs(rdir)

        with open(setting_json, 'w') as strm:
            strm.write(json.dumps(setting_dic))

    @classmethod
    def clear_cache_settings(cls):
        '''
        clear stored credentials in user machine 

        '''
        setting_json = cls._get_settings_file_path()
        if os.path.isfile(setting_json):
            os.unlink(setting_json)

    def get_projects(self, active_only=True, name=None, extra_fields=None, extra_filters=None, sort=None):
        '''
        returns a list of projects based on the given criteria 

        :param bool active_only:
        :param str name:
        :param [str] extra_fields:
        :param [list] extra_filters:
        :param [dict] sort:
        '''
        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        fields = ['name', 'code', 'id', 'sg_status']

        if extra_fields:
            fields.extend(extra_fields)

        filters = []

        if name:
            filters.append(['name', 'is', name])

        filters.extend(extra_filters)

        if not sort:
            sort = [{'field_name': 'name',
                     'direction': 'asc'}]

        if active_only:
            filters.append(['sg_status', 'is', 'Active'])

        return self.sg.find('Project',
                            filters,
                            fields,
                            order=sort)

    def get_assets(self, proj_ent, active_only=True, extra_fields=None, extra_filters=None, sort=None):
        '''
        list all the assets for the given project 

        :param dict proj_ent:
        :param bool active_only:
        :param [str] extra_fields:
        :param [list] extra_filters:
        :param [dict] sort:
        '''
        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        fields = ['name',
                  'code',
                  'id',
                  'sg_status_list',
                  'project',
                  'shots']

        if extra_fields:
            fields.extend(extra_fields)

        filters = [['project', 'is', proj_ent]]
        if extra_filters:
            filters.extend(extra_filters)

        if not sort:
            sort = [{'field_name': 'code', 'direction': 'asc'}]

        if active_only:
            filters.append(['sg_status_list', 'is', 'ip'])

        return self.sg.find('Asset', filters, fields, order=sort)

    def get_sequences(self, proj_ent, name=None, active_only=True, extra_fields=None, extra_filters=None, sort=None):
        '''
        pulls all the sequence data for a given Project


        :param dict proj_ent: project entity 
        :param bool active_only: default True will only list active sequences
        :param [str] extra_fields: additional fields you might want to add to the data
        :param [list] extra_filters: extra filter you might want to define
        :param [dict] sort: list of dictionaries controlling sorting the results
        '''

        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        fields = ['name',
                  'code',
                  'id',
                  'sg_status_list',
                  'project',
                  'shots']

        if extra_fields:
            fields.extend(extra_fields)

        filters = [['project', 'is', proj_ent]]

        if name:
            filters.append(['code', 'is', name])

        if extra_filters:
            filters.extend(filters)

        if not sort:
            sort = [{'field_name': 'code', 'direction': 'asc'}]

        if active_only:
            filters.append(['sg_status_list', 'is', 'ip'])

        return self.sg.find('Sequence', filters, fields, order=sort)

    def get_shots(self, seq_ent, name=None, active_only=True, extra_fields=None, extra_filters=None, sort=None):
        '''

        :param dict seq_ent:
        :param bool active_only:
        :param [str] extra_fields:
        :param [list] extra_filters:
        :param [dict] sort:
        '''
        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        filters = [['sg_sequence', 'is', seq_ent]]

        if name:
            filters.append(['code', 'is', name])

        if extra_filters:
            filters.extend(extra_filters)

        if active_only:
            filters.append(['sg_status_list', 'is', 'ip'])

        fields = ['name', 'code', 'id', 'project']
        if extra_fields:
            fields.extend(extra_fields)

        if not sort:
            sort = [{'field_name': 'code', 'direction': 'asc'}]

        return self.sg.find('Shot', filters, fields, order=sort)

    def get_tasks(self, shot_ent, extra_fields=None, extra_filters=None):
        """

        :param dict shot_ent:
        :param [str] extra_fields:
        :param [list] extra_filters:
        """
        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        filters = [['entity', 'is', shot_ent]]

        if extra_filters:
            filters.extend(extra_filters)

        fields = ['cached_display_name', 'name', 'code', 'id', 'entity', 'project']
        if extra_fields:
            fields.extend(extra_fields)

        return self.sg.find('Task', filters, fields)

    def get_task_version(self, task_ent, extra_fields=None, extra_filters=None):
        """

        :param dict task_ent:
        """
        extra_fields = extra_fields or []
        extra_filters = extra_filters or []

        fields = ['code']

        if extra_fields:
            fields.extend(extra_fields)

        filters = [['sg_task', 'is', task_ent]]
        if extra_filters:
            filters.extend(extra_filters)

        return self.sg.find('Version', filters, fields)

    def gen_unique_version_name(self, task_ent, ver_name):
        current_ver = 0
        ver_name = ver_name + '_v'
        versions = self.get_task_version(task_ent, extra_filters=[['code', 'starts_with', ver_name]])
        versions_int = [self._ffmpeg.extract_padding(ver['code']) for ver in versions if self._ffmpeg.extract_padding(ver['code'])]
        if versions_int:
            versions_int.sort(reverse=True)

            if current_ver < versions_int[0]:
                current_ver = versions_int[0]

        final_version = str(current_ver + 1)

        if len(final_version) < 4:
            final_version = final_version.zfill(4)

        return '%s%s' % (ver_name, final_version)

    def make_version_for_task(self, task_ent, ver_name, comment):
        if not 'type' in task_ent and task_ent['type'] != 'Task':
            raise ValueError('task_ent must be of type "Task"')

        fields = ['project', 'entity', 'sg_task', 'code', 'description', 'code', 'sg_path_to_frames']

        # NOTE: append version number to the media name
        ver_name = self.gen_unique_version_name(task_ent,
                                                ver_name)
        data = {
            'project': task_ent['project'],
            'code': ver_name,
            'description': comment,
            'sg_task': task_ent,
            'entity': task_ent['entity']
        }

        return self.sg.create('Version', data, fields)

    def upload_review_media(self, task_ent, media_path, comment, qt_pg=None):
        """

        :param dict task_ent:
        :param str media_path:
        :param str comment:
        :param QtWidgets.QProgressBar qt_pg:
        """
        # NOTE: small validation
        _, ext = os.path.splitext(media_path.lower())

        if not ext in self.media_formats:
            raise ValueError('%s is not a supported file format' % ext)

        if self.media_formats[ext] != 'image':
            raise NotImplementedError('only images are supported at the moment')

        # NOTE: gen render path
        temp_media_path = os.path.join(gettempdir(), 'temp_sg_upload_media.mov')
        if os.path.isfile(temp_media_path):
            os.unlink(temp_media_path)

        self._ffmpeg.image_list_to_mov(media_path,
                                       temp_media_path,
                                       qt_pg=qt_pg)

        if not os.path.isfile(temp_media_path):
            raise RuntimeError('Failed to generate temporary media %s' % temp_media_path)

        # NOTE: now that our media is ready let's upload this sucker!!!

        sg_version = self.make_version_for_task(task_ent,
                                                "%s_%s_%s" % (task_ent['entity']['name'], task_ent['cached_display_name'], 'Sub2D'),  # NOTE: you can come up with cooler way to name your media
                                                comment)

        try:
            # NOTE: uploading some stuff baby boy!!!
            self.sg.upload('Version',
                           sg_version['id'],
                           temp_media_path,
                           'sg_uploaded_movie',
                           os.path.basename(temp_media_path))
        except ShotgunError as msg:
            self.sg.delete('Version', sg_version['id'])
            raise msg


if __name__ == '__main__':
    print(Sub2DAPI._get_settings_file_path())
