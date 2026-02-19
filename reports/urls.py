from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.StaffDashboardView.as_view(), name='dashboard'),
    path('dashboard/student/', views.StudentDashboardView.as_view(), name='student_dashboard'),
    path('dashboard/overview/', views.dashboard_overview, name='overview'),
    path('report-issue/', views.report_issue, name='report_issue'),
    path('api/chart-data/', views.chart_data, name='chart_data'),
    path('export/csv/', views.export_tickets_csv, name='export_csv'),
]
