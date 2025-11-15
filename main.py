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
    from rich.table import Table
    from rich.columns import Columns
except ImportError:
    Console = None


def show_dashboard_summary(console, df, stats, local_corr, historical_corr):
    """
    Muestra un mini dashboard con:
    - líneas procesadas
    - alertas totales e internas
    - top IPs / usuarios
    - correlaciones locales e históricas
    """

    total_lines = len(df)
    total_alerts = stats.get("total", 0)

    # cantidades de correlaciones
    local_count = len(local_corr) if local_corr is not None and not local_corr.empty else 0
    hist_count = (
        len(historical_corr)
        if historical_corr is not None and not historical_corr.empty
        else 0
    )

    by_type = stats.get("by_type", {})
    top_ips = stats.get("top_ips", {})
    top_users = stats.get("top_users", {})

    # ---- Regla separadora tipo título ----
    console.print()
    console.rule("[bold cyan]🛡️  Log Sentinel – Dashboard[/bold cyan]")

    # -------- Panel 1: Resumen básico --------
    stats_table = Table(show_header=True, header_style="bold cyan")
    stats_table.add_column("Métrica")
    stats_table.add_column("Valor", justify="right")

    stats_table.add_row("Líneas procesadas", str(total_lines))
    stats_table.add_row("Alertas totales", str(total_alerts))
    stats_table.add_row("Correlaciones locales", str(local_count))
    stats_table.add_row("Correlaciones históricas", str(hist_count))

    stats_panel = Panel(stats_table, title="📊 Resumen", border_style="cyan")

    # -------- Panel 2: Alertas por tipo --------
    alert_table = Table(show_header=True, header_style="bold yellow")
    alert_table.add_column("Tipo")
    alert_table.add_column("Cantidad", justify="right")

    for alert_type, count in by_type.items():
        alert_table.add_row(alert_type, str(count))

    alert_panel = Panel(alert_table, title="🚨 Alertas por tipo", border_style="yellow")

    # mostramos primera fila de paneles
    console.print(Columns([stats_panel, alert_panel]))

    # -------- Panel 3: Top IPs --------
    ip_table = Table(show_header=True, header_style="bold magenta")
    ip_table.add_column("IP")
    ip_table.add_column("Alertas", justify="right")

    for ip, count in top_ips.items():
        ip_table.add_row(ip, str(count))

    ip_panel = Panel(ip_table, title="🌐 Top IPs", border_style="magenta")

    # -------- Panel 4: Top Usuarios --------
    user_table = Table(show_header=True, header_style="bold green")
    user_table.add_column("Usuario")
    user_table.add_column("Alertas", justify="right")

    for user, count in top_users.items():
        user_table.add_row(user, str(count))

    user_panel = Panel(user_table, title="👤 Top Usuarios", border_style="green")

    # segunda fila de paneles
    console.print(Columns([ip_panel, user_panel]))

    # -------- Panel 5: Resumen de correlaciones --------
    corr_lines = []
    corr_lines.append(
        f"[cyan]Correlaciones locales failed→success:[/cyan] [bold]{local_count}[/bold]"
    )
    corr_lines.append(
        f"[magenta]Correlaciones históricas brute_force→success:[/magenta] [bold]{hist_count}[/bold]"
    )

    corr_body = "\n".join(corr_lines)
    corr_panel = Panel(corr_body, title="🔗* Correlaciones", border_style="blue")

    console.print(corr_panel)

    



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

        #  CORRELACION (local + historica)
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
