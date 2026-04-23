from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import TeamForm
from .models import Team


User = get_user_model()


class TeamFormTests(TestCase):
    def setUp(self):
            self.user1 = User.objects.create(username="user1", email="user1@gmail.com",
                                             password="user1password", type="leader", skills="Django, Python")
            
            self.form_data = {"name": "team1", "max_members": 5, "leader": None}


    def test_creator_is_added_as_member(self):
          form = TeamForm(data=self.form_data, creator=self.user1)
          form.is_valid()
          team = form.save()

          self.assertIn(self.user1, team.members.all())

    
    def test_team_is_saved(self):
          form = TeamForm(data=self.form_data, creator=self.user1)
          form.is_valid()
          team = form.save()

          self.assertIsNotNone(Team.objects.filter(name=team.name).first())
