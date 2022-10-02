from app.fuzzing.models import HPCSystem, Project

from tests.fuzzing import FuzzingBaseTestCase


class FuzzingModelsTests(FuzzingBaseTestCase):
    """
    Test cases for the database models of the fuzzing module.
    """

    # ----------------------------------------------------------------
    #   HPCSYSTEM TESTS
    # ----------------------------------------------------------------

    def test_hpc_system_get_by_name(self):
        hpcs = HPCSystem.get_by_name(self._TEST_HPCS['name'])
        self.assertTrue(hpcs.name, self._TEST_HPCS['name'])

    # ----------------------------------------------------------------
    #   PROJECT TESTS
    # ----------------------------------------------------------------

    def test_project_to_dict(self):
        pass

    def test_project_get_creation_date(self):
        project = self._get_test_project()
        self.assertEqual(project.get_creation_date(), '01/01/2022, 00:00:00')

    def test_project_get_by_name(self):
        project = Project.get_by_name(self._TEST_PROJECT['name'])
        self.assertTrue(project.name, self._TEST_PROJECT['name'])

    def test_project_get_all_by_user(self):
        pass
