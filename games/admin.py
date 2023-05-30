from django.contrib import admin

from .models import Backlogged, Recommend, Playing, Goty

class BackloggedAdmin(admin.ModelAdmin):
    readonly_fields = ('date_added',)

class RecommendAdmin(admin.ModelAdmin):
    readonly_fields = ('date_recommended',)

admin.site.register(Backlogged, BackloggedAdmin)
admin.site.register(Recommend, RecommendAdmin)
admin.site.register(Playing)
admin.site.register(Goty)