from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('squad/', views.squad, name='squad'),
    path('player/<int:pk>/', views.player_detail, name='player_detail'),
    path('leaders/', views.leaders, name='leaders'),
    path('fixtures/', views.fixtures, name='fixtures'),
    path('results/', views.results, name='results'),
    path('gallery/', views.gallery, name='gallery'),
    path('join/', views.join, name='join'),
    path('contact/', views.contact, name='contact'),
    path('coach/', views.dashboard, name='dashboard'),
    path('coach/login/', views.login, name='login'),
    path('coach/logout/', views.logout, name='logout'),
    path('coach/registrations/', views.registrations, name='registrations'),
    path('coach/registrations/<int:pk>/<str:status>/', views.registration_action, name='registration_action'),
    path('coach/players/', views.admin_players, name='admin_players'),
    path('coach/fixtures/list/', views.admin_fixtures, name='admin_fixtures'),
    path('coach/photos/', views.admin_photos, name='admin_photos'),
    path('coach/add/<str:kind>/', views.add, name='add'),
    path('coach/delete/<str:kind>/<int:pk>/', views.delete, name='delete'),
    path('coach/player/<int:pk>/<str:field>/<str:step>/', views.bump, name='bump'),
    path('coach/fixture/<int:pk>/result/', views.result, name='result'),
]
