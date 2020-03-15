from django.urls import path
from . import views

urlpatterns = [
    # Обработчики действий со статьями.
    path('login/', views.user_login, name='login'),
]
