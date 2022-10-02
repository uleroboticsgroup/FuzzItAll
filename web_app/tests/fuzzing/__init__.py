from datetime import datetime

from app.fuzzing.models import HPCSystem, Project

from tests import BaseTestCase


class FuzzingBaseTestCase(BaseTestCase):
    """
    TODO: description.
    """

    _TEST_HPCS = dict(
        name='test', host='localhost', port=0, user='test', password='test'
    )
    _TEST_PROJECT = dict(
        name='test', url='localhost/test.git',
        created_on=datetime(year=2022, month=1, day=1,
                            hour=0, minute=0, second=0)
    )

    # ----------------------------------------------------------------
    #   SETUP AND TEARDOWN
    # ----------------------------------------------------------------

    def setUp(self):
        super().setUp()
        self._create_test_hpcs()
        self._create_test_project()

    # ----------------------------------------------------------------
    #   HELPER METHODS
    # ----------------------------------------------------------------

    def _create_test_hpcs(self):
        test_hpcs = HPCSystem(**self._TEST_HPCS)
        test_hpcs.save()

    def _create_test_project(self):
        test_project_data = self._TEST_PROJECT
        test_project_data['user_id'] = self._get_test_user().id
        test_project_data['hpcs_id'] = self._get_test_hpc_system().id
        test_project = Project(**test_project_data)
        test_project.save()

    def _get_test_hpc_system(self) -> HPCSystem:
        hpcs = HPCSystem.get_by_name(self._TEST_HPCS['name'])
        self.assertIsNotNone(hpcs)
        return hpcs

    def _get_test_project(self) -> Project:
        project = Project.get_by_name(self._TEST_PROJECT['name'])
        self.assertIsNotNone(project)
        return project
