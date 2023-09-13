from django.contrib import admin

from .models import Goty, Library

class RecommendAdmin(admin.ModelAdmin):
    readonly_fields = ('date_recommended',)

class LibraryAdmin(admin.ModelAdmin):
    list_display = (
        '__str__',
        'status',
        'price',
        'date_released',
        'date_backlogged',
        'date_started',
        'date_completed',
    )

admin.site.register(Goty)
admin.site.register(Library, LibraryAdmin)