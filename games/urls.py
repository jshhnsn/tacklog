from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('backlog/', views.backlog, name='backlog'),
    path('what-to-play/', views.play_next, name='what-to-play'),
]