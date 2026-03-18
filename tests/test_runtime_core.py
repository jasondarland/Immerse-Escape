from pathlib import Path
import unittest

from immerse_runtime.services.device_registry import DeviceRegistry
from immerse_runtime.services.event_logger import EventLogger
from immerse_runtime.services.logic_engine import LogicEngine
from immerse_runtime.services.alert_manager import AlertManager
from immerse_runtime.services.output_dispatcher import OutputDispatcher
from immerse_runtime.services.package_loader import PackageLoader
from immerse_runtime.services.state_manager import StateManager


class RuntimeCoreTests(unittest.TestCase):
    def setUp(self):
        self.package = PackageLoader().load(Path('demo_package'))

    def test_package_loader_reads_demo_package(self):
        self.assertEqual(self.package.name, 'IMMERSE Demo Runtime Package')
        self.assertEqual(len(self.package.devices), 8)
        self.assertIn('Atrium', self.package.project['rooms'])

    def test_logic_engine_processes_keypad_and_rfid(self):
        state = StateManager(); state.load(self.package.states)
        registry = DeviceRegistry(); registry.load(self.package.devices)
        logger = EventLogger(); alerts = AlertManager(); outputs = OutputDispatcher()
        logic = LogicEngine(state, outputs, logger, alerts, registry)
        logic.load(self.package.logic_graph)
        logic.process_trigger('keypad_correct', 'Atrium')
        logic.process_trigger('rfid_presented', 'Laboratory')
        self.assertTrue(state.get_value('atrium_keypad_solved'))
        self.assertTrue(state.get_value('lab_rfid_solved'))
        self.assertEqual(registry.devices['atrium_lock'].current_state, 'unlocked')
        self.assertEqual(len(outputs.active_outputs), 3)
        self.assertEqual(len(logger.events), 2)


if __name__ == '__main__':
    unittest.main()
