# correlator.py

import os
from datetime import timedelta

import pandas as pd

ALERTS_DIR = "alerts"


class LogCorrelator:
    """
    Motor de correlación de eventos para Log Sentinel.

    - Usa el DataFrame de eventos de la corrida actual (events_df)
    - Puede usar el historial de alertas (history_df)
    - Detecta patrones como:
        * failed_login -> successful_login (correlación local)
        * brute force histórica -> successful_login actual (correlación histórica)
    """

    def __init__(self, events_df, history_df=None):
        # Copiamos los dataframes para no modificar los originales
        self.events = events_df.copy() if events_df is not None else pd.DataFrame()
        self.history = history_df.copy() if history_df is not None else pd.DataFrame()

        # Normalizamos timestamps
        if "timestamp" in self.events.columns:
            self.events["timestamp"] = pd.to_datetime(self.events["timestamp"], errors="coerce")

        if "event_timestamp" in self.history.columns:
            self.history["event_timestamp"] = pd.to_datetime(
                self.history["event_timestamp"], errors="coerce"
            )

        # Aseguramos que exista alerts/
        os.makedirs(ALERTS_DIR, exist_ok=True)

    # ------------------------------------------------------------------ #
    # 1) CORRELACIÓN LOCAL: failed_login -> successful_login (misma IP/usuario)
    # ------------------------------------------------------------------ #
    def correlate_local(self, window_minutes=20, min_fails=1):
        """
        Busca secuencias de failed_login seguidas de successful_login
        para la misma combinación (ip, user) dentro de una ventana
        de tiempo en minutos.

        Devuelve un DataFrame con las correlaciones encontradas.
        """

        if self.events.empty:
            return pd.DataFrame()

        df = self.events.copy()

        # Nos quedamos solo con eventos de login
        login_mask = df["event"].isin(["failed_login", "successful_login"])
        df = df[login_mask].dropna(subset=["timestamp"])

        if df.empty:
            return pd.DataFrame()

        df = df.sort_values("timestamp")

        correlations = []
        window = timedelta(minutes=window_minutes)

        # Agrupamos por (ip, user) para analizar cada "par atacante/víctima"
        grouped = df.groupby(["ip", "user"], dropna=False)

        for (ip, user), group in grouped:
            fails = group[group["event"] == "failed_login"]
            successes = group[group["event"] == "successful_login"]

            if fails.empty or successes.empty:
                continue

            for _, succ in successes.iterrows():
                t_succ = succ["timestamp"]

                # Ventana hacia atrás: [t_succ - window, t_succ]
                window_fails = fails[
                    (fails["timestamp"] <= t_succ)
                    & (fails["timestamp"] >= t_succ - window)
                ]

                fail_count = len(window_fails)
                if fail_count >= min_fails:
                    correlations.append(
                        {
                            "correlation_type": "local_failed_to_success",
                            "ip": ip,
                            "user": user,
                            "failed_count": fail_count,
                            "first_fail_time": window_fails["timestamp"].min(),
                            "last_fail_time": window_fails["timestamp"].max(),
                            "success_time": t_succ,
                        }
                    )

        if not correlations:
            return pd.DataFrame()

        return pd.DataFrame(correlations)

    # ------------------------------------------------------------------ #
    # 2) CORRELACIÓN HISTÓRICA: brute force previo -> successful_login actual
    # ------------------------------------------------------------------ #
    def correlate_with_history(self, history_window_hours=24, min_alerts=1):
        """
        Cruza el historial de alertas de tipo 'bruteforce' con los
        successful_login de la corrida actual.

        Idea:
        - Si una IP/usuario tiene alertas de fuerza bruta en el historial
          y ahora vemos un successful_login, es MUY sospechoso.

        history_window_hours: cuántas horas hacia atrás miramos en el historial.
        """

        if self.events.empty or self.history.empty:
            return pd.DataFrame()

        # Successful logins actuales
        success_df = self.events[
            self.events["event"] == "successful_login"
        ].dropna(subset=["timestamp"])

        if success_df.empty:
            return pd.DataFrame()

        # Historial de brute force (alert_type='bruteforce')
        hist = self.history.copy()
        hist = hist[hist["alert_type"] == "bruteforce"].dropna(subset=["event_timestamp"])

        if hist.empty:
            return pd.DataFrame()

        hist = hist.sort_values("event_timestamp")
        window = timedelta(hours=history_window_hours)

        results = []

        for _, succ in success_df.iterrows():
            ip = succ.get("ip")
            user = succ.get("user")
            t_succ = succ["timestamp"]

            # Necesitamos IP y user para poder correlacionar
            if pd.isna(ip) or pd.isna(user):
                continue

            mask = (
                (hist["ip"] == ip)
                & (hist["user"] == user)
                & (hist["event_timestamp"] <= t_succ)
                & (hist["event_timestamp"] >= t_succ - window)
            )

            prior_alerts = hist[mask]

            if len(prior_alerts) >= min_alerts:
                results.append(
                    {
                        "correlation_type": "historical_failed_to_success",
                        "ip": ip,
                        "user": user,
                        "prior_alerts": len(prior_alerts),
                        "first_alert_time": prior_alerts["event_timestamp"].min(),
                        "last_alert_time": prior_alerts["event_timestamp"].max(),
                        "success_time": t_succ,
                    }
                )

        if not results:
            return pd.DataFrame()

        return pd.DataFrame(results)

    # ------------------------------------------------------------------ #
    # 3) Guardar resultados en CSV
    # ------------------------------------------------------------------ #
    def save_correlations(self, local_df=None, historical_df=None):
        """
        Guarda las correlaciones en CSV dentro de alerts/
        - correlated_local.csv
        - correlated_history.csv
        """

        os.makedirs(ALERTS_DIR, exist_ok=True)

        if local_df is not None and not local_df.empty:
            local_df.to_csv(
                os.path.join(ALERTS_DIR, "correlated_local.csv"),
                index=False,
            )

        if historical_df is not None and not historical_df.empty:
            historical_df.to_csv(
                os.path.join(ALERTS_DIR, "correlated_history.csv"),
                index=False,
            )
