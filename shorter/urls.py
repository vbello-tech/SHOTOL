from django.urls import path, reverse_lazy
from .views import HomeView, RedirectView, AnalyticsView
from django.contrib.auth.views import (
    PasswordResetView,
    LoginView,
)

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('<str:slug>/', RedirectView.as_view(), name="url"),
    path('analytics/<str:slug>/', AnalyticsView.as_view(), name="analytics"),
    path('login/', LoginView.as_view(
        template_name='registration/login/',
        success_url=reverse_lazy('home')
    ), name="login"),
]
