from django.urls import path

from .views import index, by_rubric, AdsCreateView

urlpatterns = [
    path('add/', AdsCreateView.as_view(), name='add'),
    path('<int:rubric_id>/', by_rubric, name='by_rubric'),
    path('', index, name='index'),
]
