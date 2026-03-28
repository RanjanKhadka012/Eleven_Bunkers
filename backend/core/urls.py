from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CardViewSet, CardTypeViewSet, CatastropheViewSet, BunkerViewSet,
    SpecialConditionViewSet, GameSessionViewSet, TextToSpeechViewSet
)

router = DefaultRouter()
router.register(r'cards', CardViewSet, basename='card')
router.register(r'card-types', CardTypeViewSet, basename='card-type')
router.register(r'catastrophes', CatastropheViewSet, basename='catastrophe')
router.register(r'bunkers', BunkerViewSet, basename='bunker')
router.register(r'special-conditions', SpecialConditionViewSet, basename='special-condition')
router.register(r'games', GameSessionViewSet, basename='game-session')
router.register(r'text-to-speech', TextToSpeechViewSet, basename='text-to-speech')

urlpatterns = [
    path('', include(router.urls)),
]
