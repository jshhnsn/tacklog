from django.contrib.auth.models import User
from django.db import models

class Goty(models.Model):
    game = models.IntegerField()
    year = models.CharField(max_length=4)
    outlet = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.outlet} awarded {self.game}'
    
class Library(models.Model):
    STATUS = [
        ('backlog','backlog'),
        ('playing','playing'),
        ('completed','completed'),
        ('retired','retired'),
    ]
    game_id = models.IntegerField()
    game_name = models.CharField(max_length=200)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default='backlog'
    )
    date_released = models.DateField(null=True, blank=True)
    date_backlogged = models.DateField(null=True, blank=True)
    date_started = models.DateField(null=True, blank=True)
    date_retired = models.DateField(null=True, blank=True)
    date_completed = models.DateField(null=True, blank=True)
    price = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Price in CAD after tax and discounts.'
    )
    platform_steam = models.BooleanField(default=False)
    platform_playstation = models.BooleanField(default=False)
    platform_switch = models.BooleanField(default=False)
    platform_xbox = models.BooleanField(default=False)
    platform_playdate = models.BooleanField(default=False)
    platform_other = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    user = models.ForeignKey(
        User,
        related_name='library',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user} added {self.game_name} ({self.game_id})'
    
    class Meta:
        unique_together = ('user', 'game_id')