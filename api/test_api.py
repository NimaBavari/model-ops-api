import unittest
from unittest.mock import MagicMock, patch

from flask import session

from .db import Session, sess
from .main import app
from .models import Model, User


class TestApi(unittest.TestCase):
    def setUp(self):
        """Set up the test client before each test."""
        self.app = app.test_client()
        self.app.testing = True
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Clean up after each test."""
        self.app_context.pop()

    @patch("app.sess.query")
    @patch("app.check_password")
    def test_login_success(self, mock_check_password, mock_query):
        """Test a successful login."""
        # Mock user data
        user = MagicMock()
        user.email_address = "test@example.com"
        user.password_hash = "hashed_password"

        mock_query.return_value.filter.return_value.one_or_none.return_value = user
        mock_check_password.return_value = True

        response = self.app.post("/login/", json={"email": "test@example.com", "password": "password123"})

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login successful", response.data)

    @patch("app.sess.query")
    def test_login_wrong_credentials(self, mock_query):
        """Test login with wrong credentials."""
        mock_query.return_value.filter.return_value.one_or_none.return_value = None

        response = self.app.post("/login/", json={"email": "wrong@example.com", "password": "wrongpassword"})

        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Wrong credentials", response.data)

    def test_login_malformed_request(self):
        """Test login with a malformed request (missing email or password)."""
        response = self.app.post("/login/", json={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Malformed request", response.data)

    def test_logout_success(self):
        """Test successful logout."""
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        response = self.app.post("/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Logout successful", response.data)
        with self.app.session_transaction() as sess:
            self.assertNotIn("current_user", sess)

    def test_logout_not_logged_in(self):
        """Test logout when not logged in."""
        response = self.app.post("/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Logout successful", response.data)

    @patch("app.sess.query")
    def test_list_users_authenticated(self, mock_query):
        """Test listing users when authenticated."""
        # Mock session and users
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        mock_query.return_value.all.return_value = [{"id": 1, "email": "user1@example.com"}]

        response = self.app.get("/users/")
        self.assertEqual(response.status_code, 200)

    def test_list_users_not_authenticated(self):
        """Test listing users when not authenticated."""
        response = self.app.get("/users/")
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Not authenticated", response.data)

    @patch("app.sess.get")
    def test_get_user_authenticated(self, mock_sess_get):
        """Test getting user when authenticated."""
        # Mock the session and user
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        mock_sess_get.return_value = {"id": 1, "email": "user1@example.com"}

        response = self.app.get("/users/1/")
        self.assertEqual(response.status_code, 200)

    @patch("app.sess.get")
    def test_get_user_not_found(self, mock_sess_get):
        """Test get user with non-existent user_id."""
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        mock_sess_get.return_value = None
        response = self.app.get("/users/999/")
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Not found", response.data)

    @patch("app.sess.get")
    @patch("app.sess.query")
    def test_list_models_authenticated(self, mock_query, mock_sess_get):
        """Test listing models for a user when authenticated."""
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        mock_sess_get.return_value = {"id": 1, "email": "test@example.com"}
        mock_query.return_value.filter.return_value.all.return_value = [{"id": 1, "name": "Model 1"}]

        response = self.app.get("/users/1/models/")
        self.assertEqual(response.status_code, 200)

    @patch("app.sess.get")
    def test_list_models_not_authenticated(self, mock_sess_get):
        """Test listing models for a user when not authenticated."""
        response = self.app.get("/users/1/models/")
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Not authenticated", response.data)

    @patch("app.sess.get")
    @patch("app.sess.query")
    @patch("app.eval")
    def test_predict_with_model(self, mock_eval, mock_query, mock_sess_get):
        """Test predicting with a model when authenticated."""
        with self.app.session_transaction() as sess:
            sess["current_user"] = {"id": 1, "email": "test@example.com"}

        mock_sess_get.return_value = {"id": 1, "email": "test@example.com"}
        model = MagicMock()
        model.algorithm = "MockAlgorithm"
        model.inputs = [1, 2, 3]
        model.weights = [0.1, 0.2, 0.3]

        mock_query.return_value.filter.return_value.all.return_value = [model]
        mock_eval.return_value = 0.5

        response = self.app.get("/users/1/models/1/predict/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"output", response.data)

    @patch("app.sess.get")
    def test_predict_with_model_not_authenticated(self, mock_sess_get):
        """Test predicting with a model when not authenticated."""
        response = self.app.get("/users/1/models/1/predict/")
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Not authenticated", response.data)


if __name__ == "__main__":
    unittest.main()
