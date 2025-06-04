import logging
from typing import Dict, Any, Optional
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

logger = logging.getLogger(__name__)


def generate_pdf_report(diagnostic_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
    """
    Gera um relatório PDF a partir dos dados de diagnóstico usando reportlab.
    
    Args:
        diagnostic_data: Dados do diagnóstico
        output_path: Caminho de saída para o PDF (opcional)
        
    Returns:
        str: Caminho do arquivo PDF gerado
        
    Raises:
        Exception: Se houver erro na geração do PDF
    """
    try:
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"diagnostic_report_{timestamp}.pdf"
            
        logger.info(f"Gerando relatório PDF: {output_path}")
        
        # Configuração do documento
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Título
        title_style = styles['Heading1']
        title_style.alignment = 1  # Centralizado
        elements.append(Paragraph("Relatório de Diagnóstico TechZe", title_style))
        elements.append(Spacer(1, 20))
        
        # Data e hora
        date_style = styles['Normal']
        date_style.alignment = 1  # Centralizado
        elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", date_style))
        elements.append(Spacer(1, 30))
        
        # Informações gerais
        elements.append(Paragraph("Informações Gerais", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Tabela de informações gerais
        general_data = [
            ["Status", diagnostic_data.get('status', 'N/A')],
            ["Score de Saúde", f"{diagnostic_data.get('health_score', 'N/A')}%"],
            ["Tempo de Execução", f"{diagnostic_data.get('execution_time', 'N/A')} segundos"],
            ["ID do Dispositivo", diagnostic_data.get('device_id', 'N/A')],
        ]
        
        general_table = Table(general_data, colWidths=[200, 300])
        general_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(general_table)
        elements.append(Spacer(1, 20))
        
        # Gráfico de saúde do sistema (se disponível)
        if 'health_score' in diagnostic_data:
            elements.append(Paragraph("Saúde do Sistema", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            # Criar gráfico de pizza
            drawing = Drawing(400, 200)
            health_score = float(diagnostic_data.get('health_score', 0))
            pie = Pie()
            pie.x = 150
            pie.y = 50
            pie.width = 100
            pie.height = 100
            pie.data = [health_score, 100 - health_score]
            pie.labels = [f'Saúde {health_score}%', f'Problemas {100 - health_score}%']
            pie.slices.strokeWidth = 0.5
            pie.slices[0].fillColor = colors.green
            pie.slices[1].fillColor = colors.red
            drawing.add(pie)
            elements.append(drawing)
            elements.append(Spacer(1, 20))
        
        # Métricas do sistema
        elements.append(Paragraph("Métricas do Sistema", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        # Tabela de métricas
        metrics_data = [
            ["Métrica", "Valor", "Status"],
        ]
        
        # CPU
        cpu_usage = diagnostic_data.get('cpu_usage', 'N/A')
        cpu_status = 'Normal' if isinstance(cpu_usage, (int, float)) and cpu_usage < 80 else 'Atenção'
        metrics_data.append(["CPU", f"{cpu_usage}%", cpu_status])
        
        # Memória
        memory_usage = diagnostic_data.get('memory_usage', 'N/A')
        memory_status = 'Normal' if isinstance(memory_usage, (int, float)) and memory_usage < 80 else 'Atenção'
        metrics_data.append(["Memória", f"{memory_usage}%", memory_status])
        
        # Disco
        disk_usage = diagnostic_data.get('disk_usage', 'N/A')
        disk_status = 'Normal' if isinstance(disk_usage, (int, float)) and disk_usage < 80 else 'Atenção'
        metrics_data.append(["Disco", f"{disk_usage}%", disk_status])
        
        metrics_table = Table(metrics_data, colWidths=[150, 150, 150])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Problemas encontrados
        issues = diagnostic_data.get('issues_found', [])
        if issues:
            elements.append(Paragraph("Problemas Encontrados", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            issues_data = [["Categoria", "Severidade", "Descrição"]]
            for issue in issues:
                issues_data.append([
                    issue.get('category', 'N/A'),
                    issue.get('severity', 'N/A'),
                    issue.get('description', 'N/A')
                ])
            
            issues_table = Table(issues_data, colWidths=[100, 100, 300])
            issues_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(issues_table)
            elements.append(Spacer(1, 20))
        
        # Recomendações
        recommendations = diagnostic_data.get('recommendations', [])
        if recommendations:
            elements.append(Paragraph("Recomendações", styles['Heading2']))
            elements.append(Spacer(1, 10))
            
            for i, recommendation in enumerate(recommendations):
                elements.append(Paragraph(f"{i+1}. {recommendation}", styles['Normal']))
                elements.append(Spacer(1, 5))
        
        # Gerar o PDF
        doc.build(elements)
        
        logger.info(f"Relatório PDF gerado com sucesso: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório PDF: {str(e)}")
        raise Exception(f"Falha na geração do relatório PDF: {str(e)}")


def generate_html_report(diagnostic_data: Dict[str, Any]) -> str:
    """
    Gera um relatório HTML a partir dos dados de diagnóstico.
    
    Args:
        diagnostic_data: Dados do diagnóstico
        
    Returns:
        str: HTML do relatório
    """
    try:
        # Template básico HTML
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório de Diagnóstico</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 10px; }
                .section { margin: 20px 0; }
                .metric { margin: 10px 0; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Relatório de Diagnóstico</h1>
                <p>Gerado em: {timestamp}</p>
            </div>
            
            <div class="section">
                <h2>Informações Gerais</h2>
                <div class="metric">Status: {status}</div>
                <div class="metric">Score de Saúde: {health_score}</div>
            </div>
            
            <div class="section">
                <h2>Métricas do Sistema</h2>
                <div class="metric">CPU: {cpu_usage}%</div>
                <div class="metric">Memória: {memory_usage}%</div>
                <div class="metric">Disco: {disk_usage}%</div>
            </div>
        </body>
        </html>
        """
        
        # Preencher template com dados
        html_content = html_template.format(
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            status=diagnostic_data.get('status', 'N/A'),
            health_score=diagnostic_data.get('overall_health', 'N/A'),
            cpu_usage=diagnostic_data.get('cpu_usage', 'N/A'),
            memory_usage=diagnostic_data.get('memory_usage', 'N/A'),
            disk_usage=diagnostic_data.get('disk_usage', 'N/A')
        )
        
        return html_content
        
    except Exception as e:
        logger.error(f"Erro ao gerar relatório HTML: {str(e)}")
        raise Exception(f"Falha na geração do relatório HTML: {str(e)}")