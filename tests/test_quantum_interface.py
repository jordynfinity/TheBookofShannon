import unittest
from unittest.mock import Mock, patch
import numpy as np
import pygame
import torch
from src.gui.quantum_interface import (
    QuantumConsciousness,
    VisualConsciousness,
    AudioConsciousness,
    LogicConsciousness,
    QuantumInterface,
    QuantumParticle,
    QuantumRule
)
from src.core.config import ConfigManager

class TestQuantumConsciousness(unittest.TestCase):
    def setUp(self):
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_component_config.return_value = {
            "network": {
                "input_size": 128,
                "hidden_size": 256,
                "output_size": 64
            }
        }
        self.consciousness = QuantumConsciousness("test", self.config_manager)
        
    def test_initialization(self):
        """Test consciousness initialization"""
        self.assertEqual(self.consciousness.name, "test")
        self.assertIsNotNone(self.consciousness.quantum_state)
        self.assertIsNotNone(self.consciousness.network)
        self.assertTrue(self.consciousness.state.is_active)
        
    def test_quantum_state_update(self):
        """Test quantum state evolution"""
        initial_phase = self.consciousness.quantum_state["phase"]
        initial_amplitude = self.consciousness.quantum_state["amplitude"]
        
        self.consciousness.update()
        
        self.assertGreater(self.consciousness.quantum_state["phase"], initial_phase)
        self.assertLess(abs(self.consciousness.quantum_state["amplitude"]), abs(initial_amplitude))
        
    def test_resource_optimization(self):
        """Test resource optimization"""
        with patch.object(self.consciousness, '_get_cpu_usage', return_value=0.9):
            self.consciousness.optimize_resources()
            self.assertLess(self.consciousness.quantum_state["energy"], 1.0)
            
    def test_config_management(self):
        """Test configuration loading and saving"""
        config = self.consciousness.save_config()
        self.assertIn("quantum_state", config)
        self.assertIn("network", config)
        
        self.consciousness.load_config(config)
        self.assertEqual(self.consciousness.quantum_state, config["quantum_state"])

class TestVisualConsciousness(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_component_config.return_value = {
            "visual_network": {
                "input_channels": 3,
                "hidden_channels": 32,
                "output_channels": 3
            }
        }
        self.consciousness = VisualConsciousness("visual", self.config_manager)
        
    def tearDown(self):
        pygame.quit()
        
    def test_particle_creation(self):
        """Test quantum particle creation"""
        initial_count = len(self.consciousness.particles)
        self.consciousness.quantum_state["amplitude"] = 1.0 + 0j
        self.consciousness._create_particles()
        self.assertGreater(len(self.consciousness.particles), initial_count)
        
    def test_particle_update(self):
        """Test particle state updates"""
        particle = QuantumParticle(
            position=np.array([400, 300]),
            velocity=np.array([10, 10]),
            energy=1.0
        )
        self.consciousness.particles.append(particle)
        
        initial_position = particle.position.copy()
        self.consciousness._update_particles()
        
        self.assertFalse(np.array_equal(particle.position, initial_position))
        self.assertLess(particle.energy, 1.0)

class TestAudioConsciousness(unittest.TestCase):
    def setUp(self):
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_component_config.return_value = {
            "audio_network": {
                "input_size": 1024,
                "hidden_size": 512,
                "output_size": 1024
            }
        }
        self.consciousness = AudioConsciousness("audio", self.config_manager)
        
    def test_frequency_generation(self):
        """Test audio frequency generation"""
        initial_frequencies = self.consciousness.frequencies.copy()
        self.consciousness.quantum_state["amplitude"] = 1.0 + 0j
        self.consciousness._create_frequencies()
        self.assertFalse(np.array_equal(self.consciousness.frequencies, initial_frequencies))
        
    def test_frequency_update(self):
        """Test frequency spectrum updates"""
        initial_frequencies = self.consciousness.frequencies.copy()
        self.consciousness._update_frequencies()
        self.assertFalse(np.array_equal(self.consciousness.frequencies, initial_frequencies))

class TestLogicConsciousness(unittest.TestCase):
    def setUp(self):
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_component_config.return_value = {
            "logic_network": {
                "input_size": 64,
                "hidden_size": 128,
                "output_size": 32
            }
        }
        self.consciousness = LogicConsciousness("logic", self.config_manager)
        
    def test_rule_generation(self):
        """Test quantum rule generation"""
        self.consciousness.states = {"test": True}
        initial_rules = len(self.consciousness.rules)
        self.consciousness.quantum_state["amplitude"] = 1.0 + 0j
        self.consciousness._generate_rules()
        self.assertGreater(len(self.consciousness.rules), initial_rules)
        
    def test_rule_execution(self):
        """Test rule execution"""
        def condition(states):
            return states.get("test") == True
            
        def action(states):
            states["test"] = False
            
        rule = QuantumRule(condition, action)
        self.consciousness.states = {"test": True}
        self.consciousness.rules = [rule]
        
        self.consciousness._update_states()
        self.assertFalse(self.consciousness.states["test"])

class TestQuantumInterface(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.interface = QuantumInterface()
        
    def tearDown(self):
        pygame.quit()
        
    def test_consciousness_initialization(self):
        """Test interface consciousness initialization"""
        self.assertIn("visual", self.interface.consciousnesses)
        self.assertIn("audio", self.interface.consciousnesses)
        self.assertIn("logic", self.interface.consciousnesses)
        
        for consciousness in self.interface.consciousnesses.values():
            self.assertTrue(consciousness.state.is_active)
            
    def test_interface_update(self):
        """Test interface update cycle"""
        visual = self.interface.consciousnesses["visual"]
        audio = self.interface.consciousnesses["audio"]
        logic = self.interface.consciousnesses["logic"]
        
        initial_visual_phase = visual.quantum_state["phase"]
        initial_audio_phase = audio.quantum_state["phase"]
        initial_logic_phase = logic.quantum_state["phase"]
        
        self.interface.update(0.016)  # Simulate 60 FPS
        
        self.assertGreater(visual.quantum_state["phase"], initial_visual_phase)
        self.assertGreater(audio.quantum_state["phase"], initial_audio_phase)
        self.assertGreater(logic.quantum_state["phase"], initial_logic_phase)
        
    def test_resource_optimization(self):
        """Test interface resource optimization"""
        with patch.object(VisualConsciousness, 'check_resources', return_value={"cpu": 0.9, "memory": 0.5, "gpu": 0.5}):
            self.interface.update(0.016)
            visual = self.interface.consciousnesses["visual"]
            self.assertLess(visual.quantum_state["energy"], 1.0)
            
    def test_improvement_generation(self):
        """Test interface improvement generation"""
        with patch.object(QuantumConsciousness, 'generate_improvements', return_value=[{"type": "test"}]):
            with patch.object(QuantumConsciousness, 'validate_improvement', return_value=True):
                with patch.object(QuantumConsciousness, 'apply_improvement', return_value=True):
                    self.interface.update(0.016)
                    # Verify improvements were applied
                    for consciousness in self.interface.consciousnesses.values():
                        consciousness.apply_improvement.assert_called_once()

if __name__ == '__main__':
    unittest.main() 