from dotenv import load_dotenv
import os
from unittest import TestCase
import unittest
from models import db, User
load_dotenv()
LOCAL_DB = os.getenv('LOCAL_DB')
os.environ.get('SUPABASE_DB_URL', f'postgresql://tarvis:{LOCAL_DB}@localhost:5432/jam_space')


# Import app

from app import app


db.create_all()


class UserModelTestCase(TestCase):

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        u1 = User.signup("test1", "email1@email.com", "password", None, "fan")
        uid1 = 1111
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None, "musician")
        uid2 = 2222
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    
    def test_user_model(self):

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            user_type="fan"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no posts & no followers
        self.assertEqual(len(u.posts), 0)
        self.assertEqual(len(u.followers), 0)
#============================================================
#Test followers
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))
#==================================================================
# Test Sign up

    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password", None, "fan")
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))
        self.assertIn(u_test.user_type, "fan")




if __name__ == '__main__':
    unittest.main()