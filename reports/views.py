from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.utils import timezone

import io
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4


class DashboardStatsView(APIView):
    """
    GET /api/dashboard/stats/  -> Estatísticas
    GET /api/dashboard/export/pdf/ -> Exporta relatório em PDF
    GET /api/dashboard/export/excel/ -> Exporta relatório em Excel
    """

    def get(self, request, *args, **kwargs):
        stats = self.get_stats()
        return Response(stats, status=status.HTTP_200_OK)

    def get_stats(self):
        # Exemplo — troque pelos dados do seu projeto
        return {
            "total_orders": 42,
            "total_products": 150,
            "active_warehouses": 3,
            "generated_at": timezone.now().isoformat(),
        }


# ---------------------------
# EXPORTAÇÃO EM PDF
# ---------------------------

class DashboardExportPDF(APIView):

    def get(self, request, *args, **kwargs):
        stats = DashboardStatsView().get_stats()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()

        story = []
        story.append(Paragraph("📊 Relatório de Estatísticas", styles["Title"]))
        story.append(Spacer(1, 20))

        for key, value in stats.items():
            story.append(Paragraph(f"<b>{key}:</b> {value}", styles["Normal"]))
            story.append(Spacer(1, 10))

        doc.build(story)

        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="relatorio.pdf"'

        return response


# ---------------------------
# EXPORTAÇÃO EM EXCEL
# ---------------------------

class DashboardExportExcel(APIView):

    def get(self, request):
        stats = DashboardStatsView().get_stats()

        df = pd.DataFrame([stats])  # 1 linha

        output = io.BytesIO()
        df.to_excel(output, index=False)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="relatorio.xlsx"'

        return response
