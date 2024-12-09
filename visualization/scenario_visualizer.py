import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class ScenarioVisualizer:
    def __init__(self):
        self.color_scheme = {
            'base': '#2C3E50',      # Azul oscuro
            'optimista': '#27AE60',  # Verde
            'pesimista': '#E74C3C',  # Rojo
            'background': '#F7F9F9', # Gris muy claro
            'grid': '#EAEDED'        # Gris claro
        }
        
        # Configuración común para todos los gráficos
        self.common_layout = {
            'font': {
                'family': "Arial, sans-serif",
                'size': 12,
                'color': "#2C3E50"
            },
            'plot_bgcolor': self.color_scheme['background'],
            'paper_bgcolor': 'white',
            'showlegend': True,
            'margin': dict(t=80, b=40, l=60, r=40),
            'template': 'plotly_white',
            'xaxis': {
                'showgrid': True,
                'gridcolor': self.color_scheme['grid'],
                'tickfont': {'size': 10},
            },
            'yaxis': {
                'showgrid': True,
                'gridcolor': self.color_scheme['grid'],
                'tickfont': {'size': 10},
            }
        }

    def _convert_to_float(self, value) -> float:
        """Convierte un valor a float, manejando porcentajes y strings"""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            if '%' in value:
                return float(value.strip('%'))
            return float(value.replace(',', ''))
        return 0.0

    def _format_metric_name(self, metric: str) -> str:
        """Formatea el nombre de la métrica para mostrar"""
        return metric.replace('_', ' ').title()

    def create_metrics_dashboard(self, scenarios: Dict[str, Any], metrics: List[str]) -> go.Figure:
        """Crea un dashboard con múltiples métricas"""
        try:
            n_metrics = len(metrics)
            cols = min(2, n_metrics)
            rows = (n_metrics + 1) // 2

            fig = make_subplots(
                rows=rows,
                cols=cols,
                subplot_titles=[self._format_metric_name(metric) for metric in metrics]
            )

            for i, metric in enumerate(metrics, 1):
                row = (i - 1) // cols + 1
                col = (i - 1) % cols + 1

                for scenario_name in ['base', 'optimista', 'pesimista']:
                    value = self._convert_to_float(
                        scenarios[scenario_name]['proyecciones'].get(metric, 0)
                    )

                    fig.add_trace(
                        go.Bar(
                            name=scenario_name.capitalize(),
                            x=[scenario_name.capitalize()],
                            y=[value],
                            marker_color=self.color_scheme[scenario_name],
                            showlegend=True if i == 1 else False
                        ),
                        row=row,
                        col=col
                    )

            fig.update_layout(
                height=300 * rows,
                width=1000,
                title='Dashboard de Métricas por Escenario',
                barmode='group',
                **self.common_layout
            )

            return fig
        except Exception as e:
            logger.error(f"Error creando dashboard de métricas: {str(e)}")
            raise

    def create_comparison_chart(self, scenarios: Dict[str, Any], metric: str) -> go.Figure:
        """Crea un gráfico comparativo de una métrica específica"""
        try:
            values = [
                self._convert_to_float(scenarios[scenario]['proyecciones'].get(metric, 0))
                for scenario in ['base', 'optimista', 'pesimista']
            ]

            fig = go.Figure(data=[
                go.Bar(
                    x=['Base', 'Optimista', 'Pesimista'],
                    y=values,
                    marker_color=[
                        self.color_scheme['base'],
                        self.color_scheme['optimista'],
                        self.color_scheme['pesimista']
                    ]
                )
            ])

            layout = self.common_layout.copy()
            layout.update({
                'title': f'Comparación de {self._format_metric_name(metric)} por Escenario',
                'showlegend': False,
                'height': 400,
                'xaxis_title': 'Escenario',
                'yaxis_title': self._format_metric_name(metric)
            })
            
            fig.update_layout(**layout)
            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico comparativo: {str(e)}")
            raise

    def create_timeline_chart(self, scenarios: Dict[str, Any], metric: str, periods: int = 4) -> go.Figure:
        """Crea un gráfico de línea temporal para una métrica"""
        try:
            fig = go.Figure()

            for scenario_name in ['base', 'optimista', 'pesimista']:
                base_value = self._convert_to_float(
                    scenarios[scenario_name]['proyecciones'].get(metric, 0)
                )
                growth_rate = self._convert_to_float(
                    scenarios[scenario_name]['proyecciones'].get(f'crecimiento_{metric}', '0%')
                ) / 100

                values = [base_value]
                for i in range(1, periods):
                    values.append(values[-1] * (1 + growth_rate))

                fig.add_trace(
                    go.Scatter(
                        x=list(range(periods)),
                        y=values,
                        name=scenario_name.capitalize(),
                        line=dict(color=self.color_scheme[scenario_name])
                    )
                )

            layout = self.common_layout.copy()
            layout.update({
                'title': f'Proyección de {self._format_metric_name(metric)} en el Tiempo',
                'height': 400,
                'xaxis_title': 'Períodos',
                'yaxis_title': self._format_metric_name(metric)
            })
            
            fig.update_layout(**layout)
            return fig

        except Exception as e:
            logger.error(f"Error creando gráfico temporal: {str(e)}")
            raise

    def export_to_html(self, fig: go.Figure, filename: str):
        """Exporta un gráfico a HTML"""
        try:
            fig.write_html(filename)
        except Exception as e:
            logger.error(f"Error exportando gráfico a HTML: {str(e)}")
            raise