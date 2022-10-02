from tests import BaseTestCase


class AuthenticationRoutesTests(BaseTestCase):
    """
    Test cases for the routes in charge of providing functionality to the
    authentication module.
    """

    __LOGIN_URL = '/auth/login'
    __LOGOUT_URL = '/auth/logout'
    __INDEX_URL = '/'
    __DASHBOARD_URL = '/dashboard'

    # ----------------------------------------------------------------
    #   TESTS
    # ----------------------------------------------------------------

    def test_show_login_page(self):
        response = self.client.get(self.__LOGIN_URL)
        self.assert_200(response)
        self.assert_template_used(name='auth/login.html')

    def test_valid_login(self):
        response = self.client.post(
            self.__LOGIN_URL, data=self._TEST_USER)
        self.assert_redirects(response, location=self.__DASHBOARD_URL)

    def test_invalid_login(self):
        req_data = self._TEST_USER
        req_data['password'] = 'Wr0ng456'
        response = self.client.post(self.__LOGIN_URL, data=req_data)
        self.assert_message_flashed('Please check username and password.')

    def test_valid_logout(self):
        self._login_test_user()
        response = self.client.get(self.__LOGOUT_URL)
        self.assert_redirects(response, location=self.__INDEX_URL)

    def test_invalid_logout(self):
        response = self.client.get(self.__LOGOUT_URL)
        self.assert_redirects(response, location=self.__INDEX_URL)
