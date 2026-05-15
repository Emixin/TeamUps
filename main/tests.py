from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.urls import reverse
from .forms import TeamForm, MySignUpForm
from .models import Team


User = get_user_model()


class TeamFormTests(TestCase):
      def setUp(self):
            self.user = User.objects.create(username="user1", email="user1@gmail.com",
                                             password="user1password", type="leader", skills="Django, Python")
            
            self.form_data = {"name": "team1", "max_members": 5, "leader": None}


      def test_creator_is_added_as_member(self):
            form = TeamForm(data=self.form_data, creator=self.user)
            form.is_valid()
            team = form.save()

            self.assertIn(self.user, team.members.all())

    
      def test_team_is_saved(self):
            form = TeamForm(data=self.form_data, creator=self.user)
            form.is_valid()
            team = form.save()

            self.assertIsNotNone(Team.objects.filter(name=team.name).first())



class MySignUpFormTests(TestCase):
      def  setUp(self):
            self.form_data = {"username": "user2", "email": "user2@gmail.com", "skills": "Django, Python, Doer, Doing, Do",
                              "password1": "user2password", "password2": "user2password", "type": "AI-PRED"}
            

      def test_user_type_is_predicted_correctly(self):
            form = MySignUpForm(data=self.form_data)
            form.is_valid()
            user = form.save()

            self.assertEqual(user.type, "DOER")


      def test_skill_field_is_not_empty(self):
            form_data = self.form_data
            form = MySignUpForm(data=form_data)
            form.is_valid()
            user = form.save()

            self.assertNotEqual(None, user.skills)
            self.assertNotEqual("", user.skills)



class DeleteUserAccountViewTests(TestCase):
      def setUp(self):
            self.client = Client()

            self.user = User.objects.create(username="user1", email="user1@gmail.com",
                                             type="leader", skills="Django, Python")
            self.user.set_password("user1password")
            self.user.save()

            self.path = reverse('delete_account')
            

      def test_user_typed_same_value(self):
            self.client.login(username="user1", password="user1password")
            
            
            same_value = {"confirm_deletion": "i want to delete my account"}
            self.client.post(self.path, same_value)

            self.assertFalse(User.objects.filter(id=self.user.id).exists())


      def user_typed_other_values(self):
            self.client.login(username="user1", password="user1password")


            wrong_value = {"confirm_deletion": "i wanna delete my account"}
            self.client.post(self.path, wrong_value)

            self.assertTrue(User.objects.filter(id=self.user.id).exists())


            uppercase_value = {"confirm_deletion": "I Want To Delete My Account"}
            self.client.post(self.path, uppercase_value)

            self.assertFalse(User.objects.filter(id=self.user.id).exists())



class HomePageViewTests(TestCase):
      def setUp(self):
            self.client = Client()


            self.user = User.objects.create(username="user3", email="user3@gmail.com",
                                             type="leader", skills="Django, Python")
            self.user.set_password("user3password")
            self.user.save()


      def test_homepage_for_unauthorized_users(self):
            respone = self.client.get(reverse("home"))
            self.assertEqual(respone.status_code, 200)


      def test_homepage_for_authorized_users(self):
            result = self.client.login(username="user3", password="user3password")
            response = self.client.get(reverse("home"))
            self.assertEqual(result, True)
            self.assertEqual(response.status_code, 200)




class ResetPasswordViewTests(TestCase):
      def setUp(self):
            self.client = Client()


            self.user = User.objects.create(username="user3", email="user3@gmail.com",
                                             type="leader", skills="Django, Python") 
            self.user.set_password("user3password")
            self.user.save()

            self.path = reverse("reset_password") + '?email=user3@gmail.com'


      def test_get_method(self):
            self.client.login(username="user3", password="user3password")
            response = self.client.get(self.path)
            self.assertEqual(response.status_code, 200)


      def test_password_is_changed_successfully(self):

            self.client.get(self.path)
            

            form_data = {"new_password": "newuser3password", "confirm_password": "newuser3password"}
            self.client.post(self.path, form_data)


            result = self.client.login(username="user3", password="newuser3password")
            self.assertTrue(result, True)


      def test_password_is_not_changed(self):
            self.client.get(self.path)
            

            form_data = {"new_password": "newuser3password", "confirm_password": "wrongpassword"}
            self.client.post(self.path, form_data)


            result = self.client.login(username="user3", password="newuser3password")
            self.assertFalse(result, True)

            result = self.client.login(username="user3", password="user3password")
            self.assertTrue(result, True)



class MyLoginViewTests(TestCase):
      def setUp(self):
            self.client = Client()

            self.user = User.objects.create(username="user3", email="user3@gmail.com",
                                             type="leader", skills="Django, Python") 
            self.user.set_password("user3password")
            self.user.save()

            self.path = reverse('login')


      def test_user_forgot_password(self):
            response = self.client.post(self.path, {'user_email': 'user@gmail.com'}, follow=True)
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, 'The email is not found!')


            response = self.client.post(self.path, {'user_email': 'user3@gmail.com'}, follow=True)
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, 'Password reset link has been sent!')


            response = self.client.post(self.path, {'user_email': 'usr3@gmail.com'})
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, 'The email is not found!')


      def test_form_validates_email(self):
            form_data = {"email_or_username": "user3@gmail.com", "password": "user3password"}

            response = self.client.post(self.path, form_data)
            self.assertEqual(response.status_code, 302)


            form_data = {"email_or_username": "usr3@gmail.com", "password": "user3password"}

            response = self.client.post(self.path, form_data)
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, "Incorrect username or password")


      def test_form_validates_username(self):
            form_data = {"email_or_username": "user3", "password": "user3password"}

            response = self.client.post(self.path, form_data)
            self.assertEqual(response.status_code, 302)


            form_data = {"email_or_username": "usr3", "password": "user3password"}

            response = self.client.post(self.path, form_data)
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, "Incorrect username or password")



class DashboardViewTests(TestCase):
      def setUp(self):
            self.client = Client()

            self.user = User.objects.create(username="user3", email="user3@gmail.com",
                                             type="leader", skills="Django, Python")
            
            self.user.set_password("user3password")
            self.user.save()

            self.team = Team.objects.create(name='team1')

            self.team.add_member(self.user)
            self.team.leader = self.user
            self.team.save()

            self.path = reverse('dashboard')


      def test_create_task(self):
            request_data = {'title': 'task1', 'deadline': '2026-12-25', 'team': self.team.id, 'task_type': 'TESTING', 'create_task': ''}

            result = self.client.login(username='user3', password='user3password')
            self.assertTrue(result)

            response = self.client.post(self.path, request_data)
            self.assertEqual(response.status_code, 302)


      # TODO: Complete this test
      def test_create_team(self):
            request_data = {'name': 'team2', 'max_members': 3, 'leader': self.user.id, 'create_team': ''}

            result = self.client.login(username='user3', password='user3password')
            self.assertTrue(result)

            response = self.client.post(self.path, request_data, follow=True)
            message_obj = list(get_messages(response.wsgi_request))[0]
            self.assertEqual(message_obj.message, "New Team Created!")


            request_data = {'name': 'team3', 'max_members': 6, 'leader': self.user.id, 'create_team': ''}

            result = self.client.login(username='user3', password='user3password')
            self.assertTrue(result)

            response = self.client.post(self.path, request_data)
            team_form_obj = response.context.get('team_form')
            [error_message] = team_form_obj.errors.as_data()['max_members'][0]
            self.assertEqual(error_message, 'Max members value should be less than five!')

