from tests import BaseTestCase


class MainRoutesTests(BaseTestCase):
    """
    Test cases for the routes in charge of providing functionality to the
    main module.
    """

    __INDEX_URL = '/'
    __DASHBOARD_URL = '/dashboard'
    __NOT_VALID_URL = '/test123456'

    # ----------------------------------------------------------------
    #   TESTS
    # ----------------------------------------------------------------

    def test_show_index_page(self):
        response = self.client.get(self.__INDEX_URL)
        self.assert_200(response)
        self.assert_template_used(name='main/index.html')

    def test_show_dashboard_page(self):
        response = self._login_test_user()
        response = self.client.get(self.__DASHBOARD_URL, follow_redirects=True)
        self.assert_200(response)
        self.assert_template_used(name='main/dashboard.html')

    def test_not_found_page(self):
        response = self.client.get(self.__NOT_VALID_URL)
        self.assert_404(response)
        self.assert_template_used(name='main/error.html')
