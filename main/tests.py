from django.test import TestCase
from django.contrib.auth import get_user_model
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
