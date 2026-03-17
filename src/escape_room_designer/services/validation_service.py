"""Validation pass for runtime-ready IMMERSE packs."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

from escape_room_designer.models.project_model import EscapeProject

SUPPORTED_PROTOCOLS = {"gpio", "mqtt", "osc", "dmx", "artnet", "sacn", "http", "tcp", "udp", "local_runtime_virtual"}


@dataclass
class ValidationIssue:
    level: str
    code: str
    message: str


@dataclass
class ValidationResult:
    passed: bool
    issues: list[ValidationIssue]

    def to_dict(self):
        return {"passed": self.passed, "issues": [asdict(i) for i in self.issues]}


class RuntimePackValidator:
    def validate(self, project: EscapeProject) -> ValidationResult:
        issues: list[ValidationIssue] = []
        room_ids = {r.room_id for r in project.layouts}

        ids = set()
        addresses = set()
        for dev in project.devices:
            if not dev.id:
                issues.append(ValidationIssue("error", "missing_device_id", f"Device '{dev.name}' missing id"))
            if dev.id in ids:
                issues.append(ValidationIssue("error", "duplicate_device_id", f"Duplicate device id '{dev.id}'"))
            ids.add(dev.id)

            if dev.address in addresses and dev.address:
                issues.append(ValidationIssue("warning", "duplicate_address", f"Duplicate device address '{dev.address}'"))
            addresses.add(dev.address)

            if dev.protocol not in SUPPORTED_PROTOCOLS:
                issues.append(ValidationIssue("error", "unsupported_protocol", f"Device '{dev.id}' has unsupported protocol '{dev.protocol}'"))
            if dev.room_id not in room_ids:
                issues.append(ValidationIssue("error", "invalid_room_reference", f"Device '{dev.id}' references unknown room '{dev.room_id}'"))
            if not dev.node_id:
                issues.append(ValidationIssue("error", "invalid_node_assignment", f"Device '{dev.id}' missing node assignment"))

        node_ids = {n.node_id for n in project.logic_nodes}
        for edge in project.logic_edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                issues.append(ValidationIssue("error", "broken_logic_link", f"Logic edge '{edge.source}->{edge.target}' is broken"))

        for cue in project.timeline:
            if not cue.target:
                issues.append(ValidationIssue("warning", "timeline_missing_target", f"Timeline cue '{cue.id}' missing target"))

        for ctrl in project.operator_controls:
            if not ctrl.get("action_type"):
                issues.append(ValidationIssue("error", "empty_operator_action", f"Control '{ctrl.get('control_id','unknown')}' missing action_type"))

        for asset in project.media:
            path = asset.get("path", "")
            if path and not Path(path).exists():
                issues.append(ValidationIssue("warning", "missing_media_file", f"Missing media file '{path}'"))

        passed = not any(i.level == "error" for i in issues)
        return ValidationResult(passed=passed, issues=issues)
