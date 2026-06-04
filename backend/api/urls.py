from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.PredictView.as_view(), name='predict'),
    path('models/', views.ModelListView.as_view(), name='model-list'),
]
