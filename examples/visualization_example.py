import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from visualization.scenario_visualizer import ScenarioVisualizer

def main():
    # Datos de ejemplo
    scenarios = {
        'base': {
            'proyecciones': {
                'ingresos': 1000000,
                'crecimiento_ingresos': '10%',
                'margen': '15%',
                'empleados': 50,
                'crecimiento_empleados': '5%'
            }
        },
        'optimista': {
            'proyecciones': {
                'ingresos': 1200000,
                'crecimiento_ingresos': '20%',
                'margen': '18%',
                'empleados': 60,
                'crecimiento_empleados': '10%'
            }
        },
        'pesimista': {
            'proyecciones': {
                'ingresos': 800000,
                'crecimiento_ingresos': '5%',
                'margen': '12%',
                'empleados': 45,
                'crecimiento_empleados': '2%'
            }
        }
    }

    # Crear visualizador
    visualizer = ScenarioVisualizer()

    # 1. Crear gráfico comparativo de ingresos
    print("Generando gráfico comparativo de ingresos...")
    fig_ingresos = visualizer.create_comparison_chart(scenarios, 'ingresos')
    visualizer.export_to_html(fig_ingresos, 'ingresos_comparison.html')

    # 2. Crear dashboard de métricas
    print("Generando dashboard de métricas...")
    metrics = ['ingresos', 'margen', 'empleados']
    fig_dashboard = visualizer.create_metrics_dashboard(scenarios, metrics)
    visualizer.export_to_html(fig_dashboard, 'metrics_dashboard.html')

    # 3. Crear gráfico de línea temporal para ingresos
    print("Generando proyección temporal de ingresos...")
    fig_timeline = visualizer.create_timeline_chart(scenarios, 'ingresos', periods=6)
    visualizer.export_to_html(fig_timeline, 'ingresos_timeline.html')

    print("\nSe han generado los siguientes archivos HTML:")
    print("- ingresos_comparison.html")
    print("- metrics_dashboard.html")
    print("- ingresos_timeline.html")

if __name__ == "__main__":
    main()