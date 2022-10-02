from app.authentication.models import User

from tests import BaseTestCase


class AuthenticationModelsTests(BaseTestCase):
    """
    Test cases for the database models of the authentication module.
    """

    def test_password_hashing(self):
        user = self._get_test_user()
        self.assertTrue(user.check_password(self._TEST_USER['password']))
        self.assertFalse(user.check_password('wrong456'))

    def test_get_by_username(self):
        valid_user = User.get_by_username(self._TEST_USER['username'])
        self.assertTrue(valid_user.username, self._TEST_USER['username'])
        invalid_user = User.get_by_username('unknown')
        self.assertIsNone(invalid_user)
