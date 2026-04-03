from django.urls import path
from . import views
from .views import OperationView, logout


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path("logout/", views.logout, name="logout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("operation/", OperationView.as_view(), name="operation-list"),
    path("operation/<int:pk>/", OperationView.as_view(), name="operation-detail"),
    path('search_person/', views.search_person, name='search_person'),
    path('create_report/', views.create_report, name='create_report'),
    path('list_reports/', views.list_reports, name='list_reports'),
    path('report/<int:report_id>/', views.report_detail, name='report-detail'),
    path('unified_search/', views.unified_search, name='unified_search'),
]