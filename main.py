# main.py

import json
from core.parser import LogParser
from core.analyzer import LogAnalyzer
from core.reporter import LogReporter
from core.alert_storage import append_alert
from core.history_reader import load_history, history_stats
from core.correlator import LogCorrelator

try:
    from rich.panel import Panel
    from rich.console import Console
except ImportError:
    Console = None


def show_dashboard_summary(console, df, stats, local_corr, historical_corr):
    """
    Muestra un panel-resumen tipo dashboard con los números clave:
    - lineas procesadas
    - alertas totales
    - alertas por tipo
    - correlaciones locales e historicas
    """
    
    total_lines = len(df)
    total_alerts = stats.get("total", 0)
    
    #cuenta la cantidad de correlaciones, si df esta vacio da 0
    local_counts = 0
    if local_corr is not None and not local_corr.empty:
        local_counts = len(local_corr)
    
    hist_counts = 0
    if historical_corr is not None and not historical_corr.empty:
        hist_counts = len(historical_corr)
    
    lines = []
    lines.append(f"[bold]Lineas procesadas:[/bold] {total_lines}")
    lines.append(f"[bold]Alertas totales:[/bold] {total_alerts}")
    lines.append("")
    
    #alerta por tipo
    lines.append("[bold]Alertas por tipo:[/bold]")
    for alert_type, count in stats.get("by_type", {}).items():
        lines.append(f"- {alert_type}: [yellow]{count}[/yellow]")
    
    lines.append("")
    lines.append(F"[bold]Correlaciones:[/bold]")
    lines.append(f"Local failed→success: [cyan]{local_counts}[/cyan]")
    lines.append(f"Históricas brute_force→success: [magenta]{hist_counts}[/magenta]")
    
    body = "\n".join(lines)
    
    console.print(
        Panel(
            body,
            title="[ Log Sentinel - Dashboard ]",
            border_style="cyan",
        )
    )
    
    



def main():
    """ punto de entrada de Log Sentinel """

    # inicializacion de console rich
    console = Console()

    # se abre el archivo y se cargan las reglas desde rules.json
    with open("rules.json", "r", encoding="utf-8") as f:
        rules = json.load(f)

    # se inicializa parser, analyzer y reporter
    log_path = "logs/sample.log"
    parser = LogParser()
    analyzer = LogAnalyzer(parser, rules=rules)
    reporter = LogReporter()

    try:
        # lee y normaliza el log en un dataframe
        df = analyzer.read_log_file(log_path)
        print(f"se procesaron {len(df)} lineas ")

        # imprime el conteo de eventos por tipo
        analyzer.summarize(df)

        # detecta eventos fuera de horario y posibles ataques de fuerza bruta
        fuera = analyzer.detect_offhour(df)
        brute, thr, win = analyzer.detect_bruteforce(df)

        print("\nEventos fuera de horario laboral:")

        # muestra los resultados
        reporter.show_offhours(fuera)
        reporter.show_bruteforce(brute, thr, win)

        # guarda las alertas detectadas en el historial
        append_alert(fuera, brute, rules=rules)

        # leer historial y calcular estadisticas
        history_df = load_history()
        stats = history_stats(history_df)

        # 🧠 CORRELACION (local + historica)
        correlator = LogCorrelator(df, history_df)

        # correlacion local: failed_login -> successful_login en la corrida actual
        local_corr = correlator.correlate_local(window_minutes=20, min_fails=1)

        # correlacion historica: brute force previo -> successful_login actual
        historical_corr = correlator.correlate_with_history(
            history_window_hours=24,
            min_alerts=1,
        )

        # guardar correlaciones en alerts/
        correlator.save_correlations(local_corr, historical_corr)

        # ------------------------------------------------------------------
        # salida en consola con rich
        # ------------------------------------------------------------------
        console.print("\n[bold cyan]Correlaciones detectadas:[/bold cyan]")

        if local_corr is not None and not local_corr.empty:
            console.print(
                f"[yellow]- Correlaciones locales failed→success:[/yellow] "
                f"[bold]{len(local_corr)}[/bold]"
            )
            for _, row in local_corr.head(3).iterrows():
                console.print(
                    f"  • [white]{row['ip']}[/white] user={row['user']} "
                    f"fails={row['failed_count']} "
                    f"[dim]({row['first_fail_time']} → {row['success_time']})[/dim]"
                )
        else:
            console.print(
                "[dim]No se detectaron correlaciones locales failed→success.[/dim]"
            )

        if historical_corr is not None and not historical_corr.empty:
            console.print(
                f"[magenta]- Correlaciones históricas brute_force→success:[/magenta] "
                f"[bold]{len(historical_corr)}[/bold]"
            )
            for _, row in historical_corr.head(3).iterrows():
                console.print(
                    f"  • [white]{row['ip']}[/white] user={row['user']} "
                    f"alertas_previas={row['prior_alerts']} "
                    f"[dim]({row['first_alert_time']} → {row['success_time']})[/dim]"
                )
        else:
            console.print(
                "[dim]No se detectaron correlaciones históricas brute_force→success.[/dim]"
            )

        # ------------------------------------------------------------------
        # resumen historico de alertas
        # ------------------------------------------------------------------
        console.print("\n[bold blue]Resumen historico de alertas:[/bold blue]")
        console.print(f"Total de alertas: [yellow]{stats['total']}[/yellow]")

        console.print("\n[bold]Alertas por tipo:[/bold]")
        for alert_type, count in stats["by_type"].items():
            console.print(f"- {alert_type}: [yellow]{count}[/yellow]")

        console.print("\n[bold]Top Ips con mas alertas:[/bold]")
        for ip, count in stats["top_ips"].items():
            console.print(f"- {ip}: [yellow]{count}[/yellow]")

        console.print("\n[bold]Top Usuarios con mas alertas:[/bold]")
        for user, count in stats["top_users"].items():
            console.print(f"- {user}: [yellow]{count}[/yellow]")

        # guarda los reportes en archivos csv
        reporter.save_report(df, "reports/full_log_report.csv")
        reporter.save_report(fuera, "alerts/offhours_report.csv")
        reporter.save_report(brute, "alerts/bruteforce_report.csv")
        
        #  Mini dashboard-resumen antes del panel final
        show_dashboard_summary(console, df, stats, local_corr, historical_corr)

        console.print(
            Panel.fit(
                "[bold green]✅ Análisis completado[/bold green]\n"
                "Reportes guardados en [yellow]reports/[/yellow] y [yellow]alerts/[/yellow]",
                title="[ Log Sentinel ]",
                border_style="green",
            )
        )

    except Exception as e:
        print(f"Error durante el procesamiento: {e}")


if __name__ == "__main__":
    main()
