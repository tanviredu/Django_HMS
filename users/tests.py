# from django.test import TestCase
# from django.contrib.auth import get_user_model()

# # Create your tests here.

# class UsersManagersTest(TestCase):
#     def test_create_user(self):
#         User = get_user_model()
#         user = user.objects.create_user(email="normal@user.com", password='foo')
#         self.assertEqual(user.email, "normal@user.com")
#         self.assertTrue(user.is_active)
#         self.assertFalse(user.is_staff)
#         self.assertFalse(user.is_superuser)

#         try:
#             self.assertIsNone(user.username)
#         except AttributeError:
#             pass
#         with self.assertRaises(TypeError):
#             User.objects.create_user()
            