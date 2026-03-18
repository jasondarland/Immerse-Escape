from __future__ import annotations

from immerse_runtime.models.entities import Severity


class LogicEngine:
    def __init__(self, state_manager, output_dispatcher, event_logger, alert_manager, device_registry) -> None:
        self.state_manager = state_manager
        self.output_dispatcher = output_dispatcher
        self.event_logger = event_logger
        self.alert_manager = alert_manager
        self.device_registry = device_registry
        self.logic_graph: dict = {}

    def load(self, logic_graph: dict) -> None:
        self.logic_graph = logic_graph

    def process_trigger(self, trigger: str, room: str, source: str = "mock") -> None:
        variables = self.state_manager.state.setdefault("variables", {})
        progression = self.state_manager.state.setdefault("progression", [])

        if trigger == "keypad_correct":
            variables["atrium_keypad_solved"] = True
            progression.append("Atrium keypad solved")
            self.output_dispatcher.dispatch("atrium_lock", room, "unlock_door", 5)
            self.device_registry.update_state("atrium_lock", "unlocked")
            self.event_logger.log(Severity.INFO, room, source, "logic", "Atrium keypad solved; unlocking vault door")
        elif trigger == "rfid_presented":
            variables["lab_rfid_solved"] = True
            progression.append("Laboratory RFID accepted")
            self.output_dispatcher.dispatch("lab_audio", room, "play_success_sting", 8)
            self.output_dispatcher.dispatch("lab_video", room, "play_reveal_sequence", 12)
            self.event_logger.log(Severity.INFO, room, source, "logic", "RFID token accepted; media cues launched")
        elif trigger == "finale_trigger":
            variables["finale_armed"] = True
            progression.append("Finale triggered")
            self.output_dispatcher.dispatch("master_lighting", room, "finale_lighting_cue", 15)
            self.event_logger.log(Severity.WARNING, room, source, "show", "Finale show sequence triggered")
        else:
            self.alert_manager.create(Severity.WARNING, source, f"Invalid or unsupported trigger '{trigger}'")
            self.event_logger.log(Severity.WARNING, room, source, "logic", f"Unsupported trigger received: {trigger}")
