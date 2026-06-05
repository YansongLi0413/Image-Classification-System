from django.urls import path
from . import views

urlpatterns = [
    path('', views.ModelListView.as_view(), name='model-list'),
    path('switch/', views.ModelSwitchView.as_view(), name='model-switch'),
    path('reload/', views.ModelReloadView.as_view(), name='model-reload'),
]
