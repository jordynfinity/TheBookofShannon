import unittest
import pygame
import sys
import os
import json
import numpy as np
import time
from unittest.mock import MagicMock, patch
from src.core.zot import FirstZot, SecondZot
from src.core.resource import ResourceManager
from src.core.config import ConfigManager
from src.core.russelian_collapse import RusselianCollapse
from src.improvement_consultant import ImprovementConsultant
import sounddevice as sd

class TestGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        pygame.init()
        cls.test_config_path = os.path.join(os.path.dirname(__file__), 'test_config.json')
        with open(cls.test_config_path, 'r') as f:
            cls.test_config = json.load(f)
        cls.config = ConfigManager()
        cls.config.set_config(cls.test_config)
        cls.resource_manager = ResourceManager()
        cls.russelian_collapse = RusselianCollapse()
        cls.improvement_consultant = ImprovementConsultant()
        
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        pygame.quit()
        if os.path.exists(cls.test_config_path):
            os.remove(cls.test_config_path)
        
    def setUp(self):
        """Set up each test"""
        self.window = None
        self.wave = None
        
    def tearDown(self):
        """Clean up after each test"""
        if self.window:
            self.window.cleanup()
        if self.wave:
            self.wave.cleanup()
            
    def test_window_initialization(self):
        """Test window initialization"""
        from src.gui.god_interface import WindowZot
        window = WindowZot("test_window", self.config)
        self.assertIsNotNone(window)
        self.assertTrue(window.state.is_active)
        self.assertTrue(window.state.is_visible)
        self.assertEqual(window.width, self.test_config['window']['width'])
        self.assertEqual(window.height, self.test_config['window']['height'])
        self.assertEqual(window.title, self.test_config['window']['title'])
        
    def test_wave_zot_creation(self):
        """Test wave Zot creation"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        self.assertIsNotNone(wave)
        self.assertTrue(wave.state.is_active)
        self.assertIsNotNone(wave.wave_state)
        self.assertEqual(wave.sample_rate, self.test_config['audio']['sample_rate'])
        self.assertEqual(len(wave.audio_buffer), self.test_config['audio']['buffer_size'])
        
    def test_wave_state_initialization(self):
        """Test wave state initialization"""
        from src.gui.god_interface import WaveState
        state = WaveState()
        self.assertEqual(state.amplitude, self.test_config['wave']['amplitude'])
        self.assertEqual(state.frequency, self.test_config['wave']['frequency'])
        self.assertEqual(state.phase, self.test_config['wave']['phase'])
        self.assertEqual(len(state.interaction_points), 0)
        
    def test_wave_update(self):
        """Test wave update functionality"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        initial_phase = wave.wave_state.phase
        wave.update()
        self.assertNotEqual(wave.wave_state.phase, initial_phase)
        self.assertGreater(wave.wave_state.phase, initial_phase)
        
    def test_interaction_handling(self):
        """Test interaction handling"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        initial_points = len(wave.wave_state.interaction_points)
        
        # Test click
        wave.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, {
            'pos': (100, 100),
            'button': 1
        }))
        self.assertEqual(len(wave.wave_state.interaction_points), initial_points + 1)
        
        # Test motion
        wave.handle_event(pygame.event.Event(pygame.MOUSEMOTION, {
            'pos': (150, 150),
            'buttons': (1, 0, 0)
        }))
        self.assertEqual(len(wave.wave_state.interaction_points), initial_points + 2)
        
        # Test interaction decay
        wave.wave_state.interaction_points[0]['timestamp'] = 0  # Old point
        wave.update()
        self.assertEqual(len(wave.wave_state.interaction_points), initial_points + 1)
        
    def test_audio_generation(self):
        """Test audio generation"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        
        # Test basic wave generation
        wave.generate_audio()
        self.assertIsNotNone(wave.audio_buffer)
        self.assertEqual(len(wave.audio_buffer), self.test_config['audio']['buffer_size'])
        self.assertTrue(np.any(wave.audio_buffer != 0))
        
        # Test harmonics
        wave.wave_state.interaction_points.append({
            'pos': (100, 100),
            'timestamp': time.time(),
            'type': 'click'
        })
        wave.generate_audio()
        self.assertTrue(np.any(wave.audio_buffer != 0))
        
    def test_resource_management(self):
        """Test resource management"""
        from src.gui.god_interface import WindowZot
        window = WindowZot("test_window", self.config)
        
        # Test metrics
        metrics = self.resource_manager.get_metrics()
        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics.cpu_percent, 0)
        self.assertLessEqual(metrics.cpu_percent, 100)
        
        # Test optimization
        with patch.object(self.resource_manager, 'optimize_resources') as mock_optimize:
            window.update()
            if metrics.cpu_percent > self.test_config['resources']['optimization_threshold'] * 100:
                mock_optimize.assert_called_once()
        
    def test_improvement_chain(self):
        """Test improvement chain integration"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        
        # Test improvement generation
        improvements = self.improvement_consultant.analyze_code(wave.__class__.__name__)
        self.assertIsNotNone(improvements)
        self.assertIsInstance(improvements, list)
        
        # Test improvement application
        if improvements:
            improvement = improvements[0]
            with patch.object(wave, 'apply_improvement') as mock_apply:
                wave.apply_improvement(improvement)
                mock_apply.assert_called_once_with(improvement)
        
    def test_russelian_validation(self):
        """Test Russelian Collapse validation"""
        from src.gui.god_interface import WaveZot
        wave = WaveZot("test_wave", self.config)
        
        # Test validation
        validation = self.russelian_collapse.validate(
            wave.__class__.__name__,
            {"type": "wave_zot"}
        )
        self.assertIsNotNone(validation)
        self.assertTrue(validation.is_valid)
        
        # Test invalid validation
        invalid_validation = self.russelian_collapse.validate(
            "invalid_code",
            {"type": "invalid"}
        )
        self.assertFalse(invalid_validation.is_valid)
        
    def test_config_integration(self):
        """Test configuration integration"""
        from src.gui.god_interface import WindowZot
        window = WindowZot("test_window", self.config)
        
        # Test config loading
        config = self.config.get_config()
        self.assertIsNotNone(config)
        self.assertIn("window", config)
        self.assertEqual(config["window"]["width"], self.test_config["window"]["width"])
        
        # Test config update
        new_config = config.copy()
        new_config["window"]["width"] = 500
        self.config.set_config(new_config)
        window = WindowZot("test_window", self.config)
        self.assertEqual(window.width, 500)
        
    def test_error_handling(self):
        """Test error handling"""
        from src.gui.god_interface import WindowZot, WaveZot
        
        # Test invalid event handling
        window = WindowZot("test_window", self.config)
        with self.assertRaises(Exception):
            window.handle_event(None)
            
        # Test invalid wave state
        wave = WaveZot("test_wave", self.config)
        with self.assertRaises(Exception):
            wave.wave_state = None
            wave.update()
            
        # Test invalid audio setup
        with patch.object(sd, 'OutputStream', side_effect=Exception("Audio error")):
            with self.assertRaises(Exception):
                WaveZot("test_wave", self.config)
                
    def test_cleanup(self):
        """Test cleanup functionality"""
        from src.gui.god_interface import WindowZot, WaveZot
        
        # Test window cleanup
        window = WindowZot("test_window", self.config)
        window.cleanup()
        self.assertFalse(window.state.is_active)
        
        # Test wave cleanup
        wave = WaveZot("test_wave", self.config)
        wave.cleanup()
        self.assertFalse(wave.state.is_active)
        self.assertFalse(hasattr(wave, 'stream'))
        
    def test_performance(self):
        """Test performance under load"""
        from src.gui.god_interface import WindowZot, WaveZot
        
        # Create multiple waves
        window = WindowZot("test_window", self.config)
        waves = [WaveZot(f"wave_{i}", self.config) for i in range(5)]
        for wave in waves:
            window.add_wave(wave)
            
        # Simulate heavy load
        for _ in range(100):
            for wave in waves:
                wave.update()
                wave.generate_audio()
            window.update()
            window.render()
            
        # Check resource usage
        metrics = self.resource_manager.get_metrics()
        self.assertLess(metrics.cpu_percent, 100)
        self.assertLess(metrics.memory_percent, 100)
        
if __name__ == '__main__':
    unittest.main() 