import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image
import pyaudio
import wave
from pydub import AudioSegment
import threading
import time
from src.living_interface import (
    LivingInterface,
    WaveState,
    ParticleSystem,
    AudioProcessor,
    SelfImprovementEngine,
    EiraCalder
)

class TestLivingInterface(unittest.TestCase):
    def setUp(self):
        self.interface = LivingInterface()
        
    def tearDown(self):
        self.interface.cleanup()
        
    def test_initialization(self):
        """Test interface initialization and state"""
        self.assertIsNotNone(self.interface.image)
        self.assertIsNotNone(self.interface.audio_stream)
        self.assertIsNotNone(self.interface.particle_system)
        self.assertIsNotNone(self.interface.wave_state)
        self.assertIsNotNone(self.interface.improvement_engine)
        self.assertIsNotNone(self.interface.eira)
        
    def test_visual_response(self):
        """Test visual response to input"""
        # Test color response
        self.interface.process_input("color", "#FF0000")
        pixel = self.interface.image.getpixel((100, 100))
        self.assertNotEqual(pixel, (0, 0, 0))
        
        # Test particle response
        self.interface.process_input("particle", {"x": 100, "y": 100, "energy": 0.8})
        particles = self.interface.particle_system.get_particles()
        self.assertTrue(any(p.x == 100 and p.y == 100 for p in particles))
        
    def test_audio_response(self):
        """Test audio response to input"""
        # Test sound generation
        self.interface.process_input("sound", {"frequency": 440, "duration": 0.5})
        audio_data = self.interface.audio_processor.get_last_audio()
        self.assertIsNotNone(audio_data)
        self.assertGreater(len(audio_data), 0)
        
        # Test wave interaction
        self.interface.process_input("wave", {"amplitude": 0.5, "frequency": 2.0})
        wave_state = self.interface.wave_state.get_state()
        self.assertGreater(wave_state.amplitude, 0)
        
    def test_self_improvement(self):
        """Test continuous self-improvement"""
        # Test improvement generation
        improvements = self.interface.improvement_engine.generate_improvements()
        self.assertGreater(len(improvements), 0)
        
        # Test improvement application
        initial_state = self.interface.get_state()
        self.interface.apply_improvement(improvements[0])
        new_state = self.interface.get_state()
        self.assertNotEqual(initial_state, new_state)
        
    def test_eira_interaction(self):
        """Test interaction with Eira Calder"""
        # Test idea sharing
        idea = self.interface.eira.share_idea("visual_enhancement")
        self.assertIsNotNone(idea)
        
        # Test improvement suggestions
        suggestions = self.interface.eira.get_suggestions()
        self.assertGreater(len(suggestions), 0)
        
    def test_state_management(self):
        """Test state management and persistence"""
        # Test state update
        self.interface.update_state({
            "color": "#00FF00",
            "sound": {"frequency": 880},
            "particles": [{"x": 200, "y": 200, "energy": 0.9}]
        })
        
        state = self.interface.get_state()
        self.assertEqual(state["color"], "#00FF00")
        self.assertEqual(state["sound"]["frequency"], 880)
        
    def test_resource_management(self):
        """Test resource management and optimization"""
        # Test memory management
        self.interface.process_input("particle", {"x": 0, "y": 0, "energy": 1.0})
        for _ in range(1000):  # Generate many particles
            self.interface.process_input("particle", {"x": 0, "y": 0, "energy": 1.0})
            
        # Verify memory optimization
        self.assertLess(len(self.interface.particle_system.get_particles()), 1000)
        
    def test_concurrent_operations(self):
        """Test concurrent operations and thread safety"""
        def input_generator():
            for _ in range(10):
                self.interface.process_input("particle", {"x": 0, "y": 0, "energy": 0.5})
                time.sleep(0.1)
                
        def improvement_generator():
            for _ in range(10):
                self.interface.improvement_engine.generate_improvements()
                time.sleep(0.1)
                
        # Run concurrent operations
        threads = [
            threading.Thread(target=input_generator),
            threading.Thread(target=improvement_generator)
        ]
        
        for thread in threads:
            thread.start()
            
        for thread in threads:
            thread.join()
            
        # Verify state consistency
        self.assertTrue(self.interface.is_state_consistent())

class TestWaveState(unittest.TestCase):
    def setUp(self):
        self.wave_state = WaveState()
        
    def test_wave_propagation(self):
        """Test wave propagation and interaction"""
        # Test wave generation
        self.wave_state.add_wave(0.5, 2.0)
        self.assertGreater(len(self.wave_state.waves), 0)
        
        # Test wave interaction
        self.wave_state.add_wave(0.3, 1.5)
        self.assertEqual(len(self.wave_state.waves), 2)
        
    def test_wave_computation(self):
        """Test wave computation and state updates"""
        # Test wave computation
        self.wave_state.add_wave(0.5, 2.0)
        self.wave_state.compute_next_state()
        
        # Verify state update
        self.assertNotEqual(self.wave_state.get_state(), self.wave_state.get_previous_state())

class TestParticleSystem(unittest.TestCase):
    def setUp(self):
        self.particle_system = ParticleSystem()
        
    def test_particle_creation(self):
        """Test particle creation and management"""
        # Test particle creation
        self.particle_system.create_particle(100, 100, 0.8)
        self.assertEqual(len(self.particle_system.get_particles()), 1)
        
        # Test particle energy
        particle = self.particle_system.get_particles()[0]
        self.assertEqual(particle.energy, 0.8)
        
    def test_particle_interaction(self):
        """Test particle interaction and behavior"""
        # Create interacting particles
        self.particle_system.create_particle(100, 100, 0.8)
        self.particle_system.create_particle(101, 101, 0.8)
        
        # Test interaction
        self.particle_system.update()
        particles = self.particle_system.get_particles()
        self.assertTrue(any(p.energy > 0.8 for p in particles))

class TestAudioProcessor(unittest.TestCase):
    def setUp(self):
        self.audio_processor = AudioProcessor()
        
    def tearDown(self):
        self.audio_processor.cleanup()
        
    def test_audio_generation(self):
        """Test audio generation and processing"""
        # Test sound generation
        audio_data = self.audio_processor.generate_sound(440, 0.5)
        self.assertIsNotNone(audio_data)
        self.assertGreater(len(audio_data), 0)
        
        # Test audio processing
        processed_data = self.audio_processor.process_audio(audio_data)
        self.assertNotEqual(processed_data, audio_data)
        
    def test_audio_interaction(self):
        """Test audio interaction with visual elements"""
        # Test audio-visual coupling
        self.audio_processor.generate_sound(440, 0.5)
        visual_response = self.audio_processor.get_visual_response()
        self.assertIsNotNone(visual_response)

class TestSelfImprovementEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SelfImprovementEngine()
        
    def test_improvement_generation(self):
        """Test improvement generation and validation"""
        # Test improvement generation
        improvements = self.engine.generate_improvements()
        self.assertGreater(len(improvements), 0)
        
        # Test improvement validation
        for improvement in improvements:
            self.assertTrue(self.engine.validate_improvement(improvement))
            
    def test_improvement_application(self):
        """Test improvement application and impact"""
        # Generate and apply improvement
        improvement = self.engine.generate_improvements()[0]
        initial_state = self.engine.get_state()
        
        self.engine.apply_improvement(improvement)
        new_state = self.engine.get_state()
        
        self.assertNotEqual(initial_state, new_state)

class TestEiraCalder(unittest.TestCase):
    def setUp(self):
        self.eira = EiraCalder()
        
    def test_idea_generation(self):
        """Test idea generation and sharing"""
        # Test idea generation
        idea = self.eira.generate_idea("visual_enhancement")
        self.assertIsNotNone(idea)
        self.assertIn("visual_enhancement", idea.tags)
        
        # Test idea sharing
        shared_ideas = self.eira.share_ideas()
        self.assertGreater(len(shared_ideas), 0)
        
    def test_improvement_suggestions(self):
        """Test improvement suggestions and validation"""
        # Test suggestion generation
        suggestions = self.eira.generate_suggestions()
        self.assertGreater(len(suggestions), 0)
        
        # Test suggestion validation
        for suggestion in suggestions:
            self.assertTrue(self.eira.validate_suggestion(suggestion))

if __name__ == '__main__':
    unittest.main() 