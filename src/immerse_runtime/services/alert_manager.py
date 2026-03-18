from __future__ import annotations

from itertools import count

from immerse_runtime.models.entities import Alert, Severity


class AlertManager:
    def __init__(self) -> None:
        self.alerts: list[Alert] = []
        self._ids = count(1)

    def create(self, severity: Severity, source: str, message: str) -> Alert:
        alert = Alert(id=f"ALT-{next(self._ids):04d}", severity=severity, source=source, message=message)
        self.alerts.append(alert)
        return alert

    def acknowledge(self, alert_id: str, note: str = "") -> None:
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                alert.resolution_notes = note
                break

    def active(self) -> list[Alert]:
        return [alert for alert in self.alerts if alert.active]
