from .models import DeviceState, Puzzle, Room, ShowElement


def build_rooms() -> list[Room]:
    return [
        Room(
            id="lab_a",
            name="Lab A",
            reset_checklist=[
                "Re-lock main entry",
                "Reset alarm panel",
                "Return keycard to start position",
            ],
            puzzles=[
                Puzzle("a_p1", "Calibrate Reactor", "pending"),
                Puzzle("a_p2", "Decode Bio Lock", "pending"),
                Puzzle("a_p3", "Stabilize Core", "pending"),
            ],
        ),
        Room(
            id="lab_b",
            name="Lab B",
            reset_checklist=[
                "Clear fog lines",
                "Reset secret panel",
                "Prime finale actuator",
            ],
            puzzles=[
                Puzzle("b_p1", "Restore Power Grid", "pending"),
                Puzzle("b_p2", "Align Satellite Dish", "pending"),
                Puzzle("b_p3", "Launch Escape Pod", "pending"),
            ],
        ),
    ]


def build_devices() -> list[DeviceState]:
    return [
        DeviceState("door_a_main", "Lab A Main Door", "lab_a", "door", "locked"),
        DeviceState("door_a_hidden", "Lab A Hidden Cabinet Lock", "lab_a", "door", "locked"),
        DeviceState("audio_a_alarm", "Lab A Alarm Sound", "lab_a", "audio", "idle"),
        DeviceState("video_a_intro", "Lab A Intro Video", "lab_a", "video", "stopped"),
        DeviceState("light_a_flash", "Lab A Red Flash Lights", "lab_a", "lighting", "idle"),
        DeviceState("fx_b_fog", "Lab B Fog Burst", "lab_b", "effects", "idle"),
        DeviceState("prop_b_panel", "Lab B Secret Panel Reveal", "lab_b", "props", "hidden"),
        DeviceState("cue_b_finale", "Lab B Finale Cue", "lab_b", "scenic", "ready"),
    ]


def build_show_elements() -> list[ShowElement]:
    return [
        ShowElement("el_1", "Unlock specific door", "lab_a", "Doors / Locks", "ready", False, True, False, "Use for manual recovery", "door_a_main"),
        ShowElement("el_2", "Lock specific door", "lab_a", "Doors / Locks", "ready", False, True, False, "Re-secure after hint", "door_a_hidden"),
        ShowElement("el_3", "Play sound effect", "lab_a", "Audio", "ready", False, True, False, "Alarm sting", "audio_a_alarm"),
        ShowElement("el_4", "Play voice line", "lab_a", "Audio", "ready", False, True, False, "GM direct hint voiceover", "audio_a_alarm"),
        ShowElement("el_5", "Start video clip", "lab_a", "Video", "ready", False, False, False, "Intro playback", "video_a_intro"),
        ShowElement("el_6", "Trigger lighting look", "lab_a", "Lighting", "ready", False, True, False, "Red flash warning look", "light_a_flash"),
        ShowElement("el_7", "Trigger fog machine", "lab_b", "Effects", "ready", True, True, False, "Use near finale only", "fx_b_fog"),
        ShowElement("el_8", "Trigger fan burst", "lab_b", "Effects", "ready", False, True, False, "Cooling pulse", "fx_b_fog"),
        ShowElement("el_9", "Move actuator / prop", "lab_b", "Props / Mechanisms", "ready", True, False, True, "Secret panel actuator", "prop_b_panel"),
        ShowElement("el_10", "Reveal clue", "lab_b", "Hints / Clues", "ready", False, False, False, "Project clue on wall", "cue_b_finale"),
        ShowElement("el_11", "Trigger finale sequence", "lab_b", "Scenic Triggers", "ready", True, False, True, "Finale timeline", "cue_b_finale"),
        ShowElement("el_12", "Blackout / Kill Effects", "lab_a", "Utility / Overrides", "ready", True, False, False, "Global safety override", ""),
    ]
