from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.PredictView.as_view(), name='predict'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('history/hot/', views.HotRecordsView.as_view(), name='history-hot'),
    path('history/<int:pk>/', views.HistoryDetailView.as_view(), name='history-detail'),
]
