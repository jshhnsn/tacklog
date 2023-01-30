from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Backlogged(models.Model):
    game = models.IntegerField()
    date_added = models.DateTimeField()
    user_id = models.ForeignKey(User, related_name='backlog', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user_id} added {self.game}'