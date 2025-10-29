from django.urls import path
from .views import HomeView, RedirectView, AnalyticsView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('<str:slug>/', RedirectView.as_view(), name="create"),
    path('analytics/<str:slug>/', AnalyticsView.as_view(), name="analytics"),
]
