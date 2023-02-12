from django.contrib.auth.models import User
from django.db import models


class Backlogged(models.Model):
    game = models.IntegerField()
    date_added = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='backlog', 
                                on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user} added {self.game}'
    

class Recommend(models.Model):
    backlog = models.ForeignKey(Backlogged, related_name='recommended', 
                                on_delete=models.CASCADE)
    date_recommended = models.DateTimeField(auto_now=True)
    user = models.ManyToManyField(User)

    def __str__(self):
        return f'{self.backlog.user} was recommended {self.backlog.game}'