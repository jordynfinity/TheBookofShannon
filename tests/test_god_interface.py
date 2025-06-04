import unittest
import numpy as np
import pygame
import time
from src.gui.god_interface import (
    GodInterface,
    VisualConsciousness,
    AudioConsciousness,
    LogicConsciousness,
    QuantumState,
    QuantumParticle
)

class TestGodInterface(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.interface = GodInterface()
        
    def tearDown(self):
        pygame.quit()
        
    def test_consciousness_initialization(self):
        """Test that all consciousnesses are properly initialized"""
        self.assertIn("visual", self.interface.consciousnesses)
        self.assertIn("audio", self.interface.consciousnesses)
        self.assertIn("logic", self.interface.consciousnesses)
        
        for name, consciousness in self.interface.consciousnesses.items():
            self.assertIsInstance(consciousness.state, QuantumState)
            self.assertEqual(consciousness.state.energy, 1.0)
            self.assertEqual(len(consciousness.state.entanglement), 2)
            
    def test_quantum_entanglement(self):
        """Test quantum entanglement between consciousnesses"""
        visual = self.interface.consciousnesses["visual"]
        audio = self.interface.consciousnesses["audio"]
        
        # Test initial entanglement
        self.assertIn(audio.name, visual.state.entanglement)
        self.assertIn(visual.name, audio.state.entanglement)
        
        # Test energy transfer
        initial_visual_energy = visual.state.energy
        initial_audio_energy = audio.state.energy
        
        visual.entangle(audio, 0.2)
        
        self.assertAlmostEqual(visual.state.energy, initial_visual_energy - 0.2)
        self.assertAlmostEqual(audio.state.energy, initial_audio_energy + 0.2)
        
    def test_visual_particle_generation(self):
        """Test visual particle generation and quantum properties"""
        visual = self.interface.consciousnesses["visual"]
        
        # Force high amplitude to trigger particle generation
        visual.state.amplitude = 1.0 + 0j
        
        # Update to generate particles
        visual.perceive(0.1)
        
        self.assertGreater(len(visual.particles), 0)
        
        for particle in visual.particles:
            self.assertIsInstance(particle, QuantumParticle)
            self.assertIsInstance(particle.quantum_state, QuantumState)
            self.assertGreater(particle.energy, 0)
            
    def test_audio_frequency_generation(self):
        """Test audio frequency generation and processing"""
        audio = self.interface.consciousnesses["audio"]
        
        # Force high amplitude to trigger frequency generation
        audio.state.amplitude = 1.0 + 0j
        
        # Update to generate frequencies
        audio.perceive(0.1)
        
        self.assertGreater(np.max(audio.frequencies), 0)
        
    def test_logic_rule_generation(self):
        """Test logic rule generation and application"""
        logic = self.interface.consciousnesses["logic"]
        
        # Add some initial states
        logic.states["test_state"] = True
        
        # Force high amplitude to trigger rule generation
        logic.state.amplitude = 1.0 + 0j
        
        # Update to generate rules
        logic.perceive(0.1)
        
        self.assertGreater(len(logic.rules), 0)
        
        # Test rule application
        for rule in logic.rules:
            if rule.condition(logic.states):
                rule.action(logic.states)
                
    def test_consciousness_interaction(self):
        """Test interaction between different consciousnesses"""
        visual = self.interface.consciousnesses["visual"]
        audio = self.interface.consciousnesses["audio"]
        logic = self.interface.consciousnesses["logic"]
        
        # Generate some initial state
        visual.state.amplitude = 1.0 + 0j
        visual.perceive(0.1)
        
        # Test visual to audio interaction
        visual.express(audio)
        self.assertGreater(np.max(audio.frequencies), 0)
        
        # Test audio to logic interaction
        audio.express(logic)
        self.assertGreater(len(logic.states), 0)
        
        # Test logic to visual interaction
        logic.express(visual)
        self.assertGreater(len(visual.effects), 0)
        
    def test_interface_update(self):
        """Test the main interface update loop"""
        initial_states = {
            name: {
                "amplitude": abs(cons.state.amplitude),
                "energy": cons.state.energy
            }
            for name, cons in self.interface.consciousnesses.items()
        }
        
        # Run update
        self.interface.update(0.1)
        
        # Check that states have evolved
        for name, cons in self.interface.consciousnesses.items():
            self.assertNotEqual(
                abs(cons.state.amplitude),
                initial_states[name]["amplitude"]
            )
            self.assertNotEqual(
                cons.state.energy,
                initial_states[name]["energy"]
            )
            
    def test_quantum_state_evolution(self):
        """Test quantum state evolution over time"""
        visual = self.interface.consciousnesses["visual"]
        initial_phase = visual.state.phase
        initial_amplitude = abs(visual.state.amplitude)
        
        # Run multiple updates
        for _ in range(10):
            visual.perceive(0.1)
            
        # Check that phase and amplitude have evolved
        self.assertNotEqual(visual.state.phase, initial_phase)
        self.assertNotEqual(abs(visual.state.amplitude), initial_amplitude)
        
    def test_neural_network_learning(self):
        """Test neural network learning capabilities"""
        visual = self.interface.consciousnesses["visual"]
        
        # Create some input data
        input_data = torch.randn(1, 128)
        
        # Get initial output
        initial_output = visual.network(input_data)
        
        # Train network
        visual.optimizer.zero_grad()
        loss = torch.nn.functional.mse_loss(initial_output, torch.randn_like(initial_output))
        loss.backward()
        visual.optimizer.step()
        
        # Get new output
        new_output = visual.network(input_data)
        
        # Check that output has changed
        self.assertFalse(torch.allclose(initial_output, new_output))
        
    def test_energy_conservation(self):
        """Test that energy is conserved in the system"""
        initial_total_energy = sum(
            cons.state.energy
            for cons in self.interface.consciousnesses.values()
        )
        
        # Run multiple updates
        for _ in range(10):
            self.interface.update(0.1)
            
        final_total_energy = sum(
            cons.state.energy
            for cons in self.interface.consciousnesses.values()
        )
        
        # Check that total energy is conserved (within floating point error)
        self.assertAlmostEqual(initial_total_energy, final_total_energy)
        
if __name__ == '__main__':
    unittest.main() 