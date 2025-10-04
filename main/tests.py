from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import TeamForm


User = get_user_model()


class TeamFormTests(TestCase):
    def setUp(self):
            self.user1 = User.objects.create(username="user1", email="user1@gmail.com", password="user1password", type="leader", skills="Django, Python")

    def test_leader_is_added_as_member(self):
          form_data = {"name": "team1", "max_members": 5, "leader": self.user1.id}
          form = TeamForm(data=form_data)
          self.assertTrue(form.is_valid())
          team = form.save()

          self.assertIn(self.user1, team.members.all())

