"""
Root URL configuration for the Survival Game project.
All API routes are delegated to the 'game' app.
"""

from django.urls import path, include

urlpatterns = [
    path('', include('game.urls')),
]
