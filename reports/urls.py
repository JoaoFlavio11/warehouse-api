from django.urls import path
from .views import DashboardStatsView, DashboardExportPDF, DashboardExportExcel

urlpatterns = [
    path("stats/", DashboardStatsView.as_view(), name="dashboard-stats"),
    path("export/pdf/", DashboardExportPDF.as_view(), name="dashboard-export-pdf"),
    path("export/excel/", DashboardExportExcel.as_view(), name="dashboard-export-excel"),
]
