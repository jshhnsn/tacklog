from django.contrib import admin

from .models import Backlogged, Recommend, Playing

class BackloggedAdmin(admin.ModelAdmin):
    readonly_fields = ('date_added',)

class RecommendAdmin(admin.ModelAdmin):
    readonly_fields = ('date_recommended',)

class PlayingAdmin(admin.ModelAdmin):
    readonly_fields = ('date_started',)

admin.site.register(Backlogged, BackloggedAdmin)
admin.site.register(Recommend, RecommendAdmin)
admin.site.register(Playing, PlayingAdmin)