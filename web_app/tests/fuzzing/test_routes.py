from tests.fuzzing import FuzzingBaseTestCase


class FuzzingRoutesTests(FuzzingBaseTestCase):
    """
    Test cases for the routes in charge of providing functionality to the
    fuzzing module.
    """

    __PROJECTS_URL = '/fuzz/projects'
    __PROJECT_DETAILS_URL = '/fuzz/projects/<project_id>'
    __PROJECT_DELETE_URL = '/fuzz/projects/<project_id>/delete'
    __PROJECT_CREATE_URL = '/fuzz/projects/create'
    __PROJECT_DOWNLOAD_URL = '/fuzz/projects/<project_id>/download'

    # ----------------------------------------------------------------
    #   SETUP AND TEARDOWN
    # ----------------------------------------------------------------

    def setUp(self):
        super().setUp()
        self._login_test_user()

    # ----------------------------------------------------------------
    #   TESTS
    # ----------------------------------------------------------------

    def test_show_projects_page(self):
        response = self.client.get(self.__PROJECTS_URL)
        self.assert_200(response)
        self.assert_template_used(name='fuzz/projects.html')

    def test_show_project_details_page(self):
        pass

    def test_show_invalid_project_details_page(self):
        pass

    def test_delete_project_page(self):
        pass

    def test_download_project_page(self):
        pass

    def test_create_project_page(self):
        pass
