from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Backlogged(models.Model):
    game = models.IntegerField()
    date_added = models.DateTimeField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __self__(self):
        return f'{self.user_id} added {self.game}'