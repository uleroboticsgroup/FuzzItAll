"""
TODO: description of test package.
"""

from flask_testing import TestCase

from app import create_app, db, bcrypt
from app.authentication.models import User


class BaseTestCase(TestCase):
    """
    Base test case upon which to build specific test cases (specifically
    for testing Flask functionality).

    Methods
    -------
    create_app():
        Creates and configures the Flask app (overriden from TestCase)
    setUp():
        Prepare the test fixture (executed prior to each test).
    tearDown():
        Free resources from the test fixture (executed after each test).
    """

    _TEST_USER = dict(username='test', password='TeSt123')

    render_templates = False

    # ----------------------------------------------------------------
    #   TestCase METHODS
    # ----------------------------------------------------------------

    def create_app(self):
        app = create_app('config.testing')
        return app

    # ----------------------------------------------------------------
    #   SETUP AND TEARDOWN
    # ----------------------------------------------------------------

    def setUp(self):
        # create the database schema
        db.create_all()
        self._create_test_user()

    def tearDown(self):
        # end db connection and erase its content
        db.session.remove()
        db.drop_all()

    # ----------------------------------------------------------------
    #   HELPER METHODS
    # ----------------------------------------------------------------

    def _create_test_user(self):
        test_user = User(
            username=self._TEST_USER['username'],
            password=bcrypt.generate_password_hash(
                self._TEST_USER['password']).decode('utf-8')
        )
        test_user.save()

    def _get_test_user(self):
        user = User.get_by_username(self._TEST_USER['username'])
        self.assertIsNotNone(user)
        return user

    def _login_test_user(self):
        return self.client.post(
            '/auth/login', data=self._TEST_USER, follow_redirects=True)
