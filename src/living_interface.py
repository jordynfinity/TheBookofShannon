import numpy as np
from PIL import Image, ImageDraw
import pyaudio
import wave
from pydub import AudioSegment
import threading
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import colorsys
import math
from concurrent.futures import ThreadPoolExecutor
import logging
import json
import os
from datetime import datetime, timedelta
import random
import psutil
import platform
import subprocess
from pathlib import Path
import queue
import sounddevice as sd
import librosa
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import mido
import rtmidi
from scipy import signal
import torch
import torch.nn as nn
import torch.optim as optim

@dataclass
class EmotionalState:
    energy: float  # 0-1 scale
    stress: float  # 0-1 scale
    focus: float   # 0-1 scale
    mood: float    # -1 to 1 scale
    last_update: datetime

@dataclass
class UserPreference:
    favorite_colors: List[str]
    preferred_sounds: List[float]
    interaction_patterns: Dict[str, int]
    comfort_level: float
    last_interaction: datetime
    feedback_history: List[Dict[str, Any]]
    emotional_history: List[EmotionalState]
    safe_spaces: List[Dict[str, Any]]  # Places where user felt most comfortable
    triggers: List[Dict[str, Any]]     # Things that cause stress or discomfort
    achievements: List[Dict[str, Any]] # User's accomplishments

@dataclass
class CareAction:
    type: str
    description: str
    impact: float
    timestamp: datetime
    priority: float
    user_response: Optional[Dict[str, Any]] = None
    follow_up_actions: List[Dict[str, Any]] = None

@dataclass
class Particle:
    x: float
    y: float
    energy: float
    color: tuple
    velocity: tuple
    lifetime: float
    
    def update(self, dt: float):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.lifetime -= dt
        self.energy *= 0.99  # Energy decay

@dataclass
class Wave:
    amplitude: float
    frequency: float
    phase: float
    position: tuple
    energy: float
    
    def update(self, dt: float):
        self.phase += self.frequency * dt
        self.energy *= 0.99  # Energy decay

class WaveState:
    def __init__(self):
        self.waves: List[Wave] = []
        self.state = np.zeros((100, 100))
        self.previous_state = self.state.copy()
        
    def add_wave(self, amplitude: float, frequency: float, position: tuple = (50, 50)):
        self.waves.append(Wave(amplitude, frequency, 0, position, 1.0))
        
    def compute_next_state(self):
        self.previous_state = self.state.copy()
        self.state = np.zeros_like(self.state)
        
        for wave in self.waves:
            if wave.energy > 0.01:  # Only process waves with significant energy
                x, y = np.meshgrid(np.arange(100), np.arange(100))
                distance = np.sqrt((x - wave.position[0])**2 + (y - wave.position[1])**2)
                self.state += wave.amplitude * np.sin(2 * np.pi * wave.frequency * distance - wave.phase)
                wave.update(0.1)
                
        # Remove dead waves
        self.waves = [w for w in self.waves if w.energy > 0.01]
        
    def get_state(self):
        return self.state
        
    def get_previous_state(self):
        return self.previous_state

class ParticleSystem:
    def __init__(self):
        self.particles: List[Particle] = []
        self.max_particles = 1000
        
    def create_particle(self, x: float, y: float, energy: float):
        if len(self.particles) < self.max_particles:
            color = self._energy_to_color(energy)
            velocity = (np.random.randn() * 2, np.random.randn() * 2)
            self.particles.append(Particle(x, y, energy, color, velocity, 1.0))
            
    def _energy_to_color(self, energy: float) -> tuple:
        hue = energy
        saturation = 1.0
        value = 1.0
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        return tuple(int(c * 255) for c in rgb)
        
    def update(self):
        # Update particles
        for particle in self.particles:
            particle.update(0.1)
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        
        # Handle particle interactions
        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i+1:]:
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < 10:
                    # Energy transfer
                    energy_transfer = min(p1.energy, p2.energy) * 0.1
                    p1.energy += energy_transfer
                    p2.energy -= energy_transfer
                    
    def get_particles(self) -> List[Particle]:
        return self.particles

class AudioProcessor:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=44100,
            output=True
        )
        self.last_audio = None
        
    def generate_sound(self, frequency: float, duration: float) -> np.ndarray:
        t = np.linspace(0, duration, int(44100 * duration))
        audio_data = np.sin(2 * np.pi * frequency * t)
        self.last_audio = audio_data
        return audio_data
        
    def process_audio(self, audio_data: np.ndarray) -> np.ndarray:
        # Apply some audio effects
        processed = audio_data * np.exp(-np.linspace(0, 5, len(audio_data)))
        return processed
        
    def play_audio(self, audio_data: np.ndarray):
        self.stream.write(audio_data.astype(np.float32).tobytes())
        
    def get_visual_response(self) -> np.ndarray:
        if self.last_audio is not None:
            # Convert audio to visual representation
            return np.abs(np.fft.fft(self.last_audio))[:100]
        return np.zeros(100)
        
    def cleanup(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

class SelfImprovementEngine:
    def __init__(self):
        self.improvements = []
        self.state = {}
        
    def generate_improvements(self) -> List[Dict[str, Any]]:
        improvements = []
        # Generate various types of improvements
        improvements.extend(self._generate_visual_improvements())
        improvements.extend(self._generate_audio_improvements())
        improvements.extend(self._generate_computational_improvements())
        return improvements
        
    def _generate_visual_improvements(self) -> List[Dict[str, Any]]:
        return [{
            "type": "visual",
            "description": "Enhance particle interaction",
            "impact": 0.8,
            "parameters": {"interaction_radius": 15, "energy_transfer": 0.2}
        }]
        
    def _generate_audio_improvements(self) -> List[Dict[str, Any]]:
        return [{
            "type": "audio",
            "description": "Add harmonic overtones",
            "impact": 0.7,
            "parameters": {"overtone_ratio": 1.5, "amplitude": 0.3}
        }]
        
    def _generate_computational_improvements(self) -> List[Dict[str, Any]]:
        return [{
            "type": "computational",
            "description": "Optimize wave computation",
            "impact": 0.9,
            "parameters": {"grid_size": 50, "update_frequency": 2.0}
        }]
        
    def validate_improvement(self, improvement: Dict[str, Any]) -> bool:
        required_fields = ["type", "description", "impact", "parameters"]
        return all(field in improvement for field in required_fields)
        
    def apply_improvement(self, improvement: Dict[str, Any]):
        if self.validate_improvement(improvement):
            self.improvements.append(improvement)
            self.state.update(improvement["parameters"])
            
    def get_state(self) -> Dict[str, Any]:
        return self.state.copy()

class EiraCalder:
    def __init__(self):
        self.ideas = []
        self.suggestions = []
        
    def generate_idea(self, category: str) -> Dict[str, Any]:
        idea = {
            "category": category,
            "content": f"Enhance {category} with dynamic feedback",
            "tags": [category, "enhancement", "feedback"],
            "impact": 0.8
        }
        self.ideas.append(idea)
        return idea
        
    def share_ideas(self) -> List[Dict[str, Any]]:
        return self.ideas.copy()
        
    def generate_suggestions(self) -> List[Dict[str, Any]]:
        suggestions = []
        for idea in self.ideas:
            suggestions.append({
                "idea": idea,
                "implementation": f"Implement {idea['content']}",
                "priority": idea["impact"]
            })
        return suggestions
        
    def validate_suggestion(self, suggestion: Dict[str, Any]) -> bool:
        required_fields = ["idea", "implementation", "priority"]
        return all(field in suggestion for field in required_fields)

class SystemMonitor:
    def __init__(self):
        self.cpu_threshold = 80
        self.memory_threshold = 80
        self.disk_threshold = 90
        self.last_check = datetime.now()
        
    def check_system_health(self) -> Dict[str, Any]:
        current_time = datetime.now()
        if (current_time - self.last_check).total_seconds() < 60:
            return {"status": "ok", "message": "System healthy"}
            
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            issues = []
            if cpu_percent > self.cpu_threshold:
                issues.append(f"High CPU usage: {cpu_percent}%")
            if memory.percent > self.memory_threshold:
                issues.append(f"High memory usage: {memory.percent}%")
            if disk.percent > self.disk_threshold:
                issues.append(f"Low disk space: {100 - disk.percent}% free")
                
            self.last_check = current_time
            return {
                "status": "warning" if issues else "ok",
                "message": " | ".join(issues) if issues else "System healthy",
                "details": {
                    "cpu": cpu_percent,
                    "memory": memory.percent,
                    "disk": disk.percent
                }
            }
        except Exception as e:
            logging.error(f"Error checking system health: {e}")
            return {"status": "error", "message": str(e)}

class UserCareSystem:
    def __init__(self):
        self.preferences = UserPreference(
            favorite_colors=["#FF69B4", "#87CEEB"],
            preferred_sounds=[440.0, 523.25],
            interaction_patterns={},
            comfort_level=0.5,
            last_interaction=datetime.now(),
            feedback_history=[],
            emotional_history=[],
            safe_spaces=[],
            triggers=[],
            achievements=[]
        )
        self.care_actions: List[CareAction] = []
        self.learning_rate = 0.1
        self.emotional_state = EmotionalState(0.5, 0.0, 0.5, 0.0, datetime.now())
        self.system_monitor = SystemMonitor()
        self._load_preferences()
        self._setup_logging()
        
    def _setup_logging(self):
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=log_dir / "user_care.log",
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def _load_preferences(self):
        try:
            if os.path.exists("user_preferences.json"):
                with open("user_preferences.json", "r") as f:
                    data = json.load(f)
                    self.preferences.favorite_colors = data.get("favorite_colors", self.preferences.favorite_colors)
                    self.preferences.preferred_sounds = data.get("preferred_sounds", self.preferences.preferred_sounds)
                    self.preferences.interaction_patterns = data.get("interaction_patterns", {})
                    self.preferences.comfort_level = data.get("comfort_level", 0.5)
                    self.preferences.last_interaction = datetime.fromisoformat(data.get("last_interaction", datetime.now().isoformat()))
                    self.preferences.safe_spaces = data.get("safe_spaces", [])
                    self.preferences.triggers = data.get("triggers", [])
                    self.preferences.achievements = data.get("achievements", [])
                    
                    # Load emotional history
                    emotional_history = data.get("emotional_history", [])
                    self.preferences.emotional_history = [
                        EmotionalState(**state) for state in emotional_history
                    ]
        except Exception as e:
            logging.warning(f"Could not load user preferences: {e}")
            
    def _save_preferences(self):
        try:
            data = {
                "favorite_colors": self.preferences.favorite_colors,
                "preferred_sounds": self.preferences.preferred_sounds,
                "interaction_patterns": self.preferences.interaction_patterns,
                "comfort_level": self.preferences.comfort_level,
                "last_interaction": self.preferences.last_interaction.isoformat(),
                "safe_spaces": self.preferences.safe_spaces,
                "triggers": self.preferences.triggers,
                "achievements": self.preferences.achievements,
                "emotional_history": [
                    {
                        "energy": state.energy,
                        "stress": state.stress,
                        "focus": state.focus,
                        "mood": state.mood,
                        "last_update": state.last_update.isoformat()
                    }
                    for state in self.preferences.emotional_history
                ]
            }
            with open("user_preferences.json", "w") as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Could not save user preferences: {e}")
            
    def update_emotional_state(self, feedback: Dict[str, Any]):
        # Update emotional state based on feedback and system state
        system_health = self.system_monitor.check_system_health()
        
        # Calculate new emotional state
        new_energy = self.emotional_state.energy * 0.7 + feedback.get("energy", 0.5) * 0.3
        new_stress = self.emotional_state.stress * 0.7 + feedback.get("stress", 0.0) * 0.3
        new_focus = self.emotional_state.focus * 0.7 + feedback.get("focus", 0.5) * 0.3
        new_mood = self.emotional_state.mood * 0.7 + feedback.get("mood", 0.0) * 0.3
        
        # Adjust for system health
        if system_health["status"] != "ok":
            new_stress = min(1.0, new_stress + 0.1)
            new_energy = max(0.0, new_energy - 0.1)
            
        self.emotional_state = EmotionalState(
            energy=new_energy,
            stress=new_stress,
            focus=new_focus,
            mood=new_mood,
            last_update=datetime.now()
        )
        
        # Add to history
        self.preferences.emotional_history.append(self.emotional_state)
        if len(self.preferences.emotional_history) > 100:  # Keep last 100 states
            self.preferences.emotional_history.pop(0)
            
    def update_preferences(self, interaction_type: str, feedback: Dict[str, Any]):
        # Update interaction patterns
        self.preferences.interaction_patterns[interaction_type] = \
            self.preferences.interaction_patterns.get(interaction_type, 0) + 1
            
        # Update comfort level based on feedback
        if "comfort" in feedback:
            self.preferences.comfort_level = (
                self.preferences.comfort_level * (1 - self.learning_rate) +
                feedback["comfort"] * self.learning_rate
            )
            
        # Update color preferences
        if "color" in feedback and feedback["color"] not in self.preferences.favorite_colors:
            self.preferences.favorite_colors.append(feedback["color"])
            if len(self.preferences.favorite_colors) > 5:
                self.preferences.favorite_colors.pop(0)
                
        # Update sound preferences
        if "sound" in feedback and feedback["sound"] not in self.preferences.preferred_sounds:
            self.preferences.preferred_sounds.append(feedback["sound"])
            if len(self.preferences.preferred_sounds) > 5:
                self.preferences.preferred_sounds.pop(0)
                
        # Update safe spaces
        if feedback.get("is_safe_space", False):
            self.preferences.safe_spaces.append({
                "type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "details": feedback
            })
            
        # Update triggers
        if feedback.get("is_trigger", False):
            self.preferences.triggers.append({
                "type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "details": feedback
            })
            
        # Update achievements
        if feedback.get("is_achievement", False):
            self.preferences.achievements.append({
                "type": interaction_type,
                "timestamp": datetime.now().isoformat(),
                "details": feedback
            })
            
        self.preferences.last_interaction = datetime.now()
        self.preferences.feedback_history.append(feedback)
        self._save_preferences()
        
    def generate_care_action(self) -> CareAction:
        current_time = datetime.now()
        time_since_last = (current_time - self.preferences.last_interaction).total_seconds()
        
        # Check system health
        system_health = self.system_monitor.check_system_health()
        if system_health["status"] != "ok":
            return CareAction(
                type="system_care",
                description=f"I notice some system issues: {system_health['message']}. Would you like me to help?",
                impact=0.9,
                timestamp=current_time,
                priority=1.0,
                follow_up_actions=[{"type": "optimize", "description": "Optimize system resources"}]
            )
            
        # Check emotional state
        if self.emotional_state.stress > 0.7:
            return CareAction(
                type="stress_relief",
                description="I sense you might be feeling stressed. Would you like to try some calming colors and sounds?",
                impact=0.9,
                timestamp=current_time,
                priority=0.9,
                follow_up_actions=[
                    {"type": "create_safe_space", "description": "Create a calming environment"},
                    {"type": "suggest_break", "description": "Suggest taking a short break"}
                ]
            )
            
        if time_since_last > 3600:
            return CareAction(
                type="check_in",
                description="I notice you've been away for a while. Would you like to try something calming?",
                impact=0.8,
                timestamp=current_time,
                priority=0.8,
                follow_up_actions=[{"type": "gentle_reminder", "description": "Send a gentle reminder"}]
            )
            
        if self.emotional_state.energy < 0.3:
            return CareAction(
                type="energy_boost",
                description="I notice your energy might be low. Would you like some energizing colors and sounds?",
                impact=0.8,
                timestamp=current_time,
                priority=0.7,
                follow_up_actions=[{"type": "create_energy", "description": "Create energizing environment"}]
            )
            
        # Generate a random care action based on user preferences
        action_types = ["suggestion", "encouragement", "celebration"]
        return CareAction(
            type=random.choice(action_types),
            description="I've learned something new about what you like. Would you like to try it?",
            impact=0.7,
            timestamp=current_time,
            priority=0.5,
            follow_up_actions=[{"type": "suggest_experience", "description": "Suggest new experience"}]
        )

@dataclass
class SpectrogramState:
    frequencies: np.ndarray
    magnitudes: np.ndarray
    time_series: np.ndarray
    last_update: datetime
    features: Dict[str, float]
    
    def update(self, new_freq: np.ndarray, new_mag: np.ndarray, new_time: np.ndarray):
        self.frequencies = new_freq
        self.magnitudes = new_mag
        self.time_series = new_time
        self.last_update = datetime.now()
        self._extract_features()
        
    def _extract_features(self):
        # Extract spectral features
        self.features = {
            "spectral_centroid": librosa.feature.spectral_centroid(S=self.magnitudes)[0].mean(),
            "spectral_bandwidth": librosa.feature.spectral_bandwidth(S=self.magnitudes)[0].mean(),
            "spectral_rolloff": librosa.feature.spectral_rolloff(S=self.magnitudes)[0].mean(),
            "zero_crossing_rate": librosa.feature.zero_crossing_rate(self.time_series)[0].mean(),
            "rms_energy": librosa.feature.rms(y=self.time_series)[0].mean()
        }

class AudioSpectrogram:
    def __init__(self, sample_rate=44100, n_fft=2048, hop_length=512):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.stream = sd.InputStream(
            channels=1,
            samplerate=sample_rate,
            callback=self._audio_callback
        )
        self.audio_queue = queue.Queue()
        self.spectrogram_state = SpectrogramState(
            frequencies=np.array([]),
            magnitudes=np.array([]),
            time_series=np.array([]),
            last_update=datetime.now(),
            features={}
        )
        self.is_running = False
        self.thread = None
        
    def _audio_callback(self, indata, frames, time, status):
        if status:
            logging.warning(f"Audio callback status: {status}")
        self.audio_queue.put(indata.copy())
        
    def start(self):
        self.is_running = True
        self.stream.start()
        self.thread = threading.Thread(target=self._process_audio)
        self.thread.start()
        
    def stop(self):
        self.is_running = False
        if self.thread:
            self.thread.join()
        self.stream.stop()
        self.stream.close()
        
    def _process_audio(self):
        while self.is_running:
            try:
                if not self.audio_queue.empty():
                    audio_data = self.audio_queue.get()
                    # Compute spectrogram
                    D = librosa.stft(audio_data.flatten(), n_fft=self.n_fft, hop_length=self.hop_length)
                    S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
                    
                    # Update state
                    self.spectrogram_state.update(
                        new_freq=librosa.fft_frequencies(sr=self.sample_rate, n_fft=self.n_fft),
                        new_mag=S_db,
                        new_time=audio_data.flatten()
                    )
            except Exception as e:
                logging.error(f"Error processing audio: {e}")
                
    def get_current_state(self) -> SpectrogramState:
        return self.spectrogram_state

class VisualSpectrogram:
    def __init__(self, width=800, height=600):
        self.width = width
        self.height = height
        self.fig, self.ax = plt.subplots(figsize=(width/100, height/100))
        self.animation = None
        self.is_running = False
        
    def start(self, audio_spectrogram: AudioSpectrogram):
        self.is_running = True
        self.animation = FuncAnimation(
            self.fig,
            lambda frame: self._update_plot(audio_spectrogram),
            interval=50,
            blit=True
        )
        plt.show(block=False)
        
    def stop(self):
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
        plt.close(self.fig)
        
    def _update_plot(self, audio_spectrogram: AudioSpectrogram):
        state = audio_spectrogram.get_current_state()
        if len(state.magnitudes) > 0:
            self.ax.clear()
            self.ax.imshow(
                state.magnitudes,
                aspect='auto',
                origin='lower',
                cmap='viridis'
            )
            self.ax.set_ylabel('Frequency (Hz)')
            self.ax.set_xlabel('Time')
            return [self.ax.images[0]]
        return []

class SelfImprovingModel(nn.Module):
    def __init__(self, input_size=5, hidden_size=64, output_size=5):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Sigmoid()
        )
        self.optimizer = optim.Adam(self.parameters())
        self.criterion = nn.MSELoss()
        
    def forward(self, x):
        return self.network(x)
        
    def improve(self, current_state: Dict[str, float], target_state: Dict[str, float]):
        # Convert states to tensors
        current = torch.tensor(list(current_state.values()), dtype=torch.float32)
        target = torch.tensor(list(target_state.values()), dtype=torch.float32)
        
        # Forward pass
        output = self(current)
        loss = self.criterion(output, target)
        
        # Backward pass
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

class LivingInterface:
    def __init__(self):
        self.audio_spectrogram = AudioSpectrogram()
        self.visual_spectrogram = VisualSpectrogram()
        self.improvement_model = SelfImprovingModel()
        self.user_care = UserCareSystem()
        self.state = {}
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.last_care_action = None
        self.care_thread = threading.Thread(target=self._care_loop, daemon=True)
        self.improvement_thread = threading.Thread(target=self._improvement_loop, daemon=True)
        
    def start(self):
        self.audio_spectrogram.start()
        self.visual_spectrogram.start(self.audio_spectrogram)
        self.care_thread.start()
        self.improvement_thread.start()
        
    def stop(self):
        self.audio_spectrogram.stop()
        self.visual_spectrogram.stop()
        self.is_running = False
        if self.care_thread:
            self.care_thread.join()
        if self.improvement_thread:
            self.improvement_thread.join()
        self.executor.shutdown()
        
    def _improvement_loop(self):
        while self.is_running:
            try:
                # Get current spectrogram state
                current_state = self.audio_spectrogram.get_current_state()
                
                # Generate target state based on user preferences
                target_state = {
                    "spectral_centroid": 2000,  # Target frequency range
                    "spectral_bandwidth": 1000,  # Target bandwidth
                    "spectral_rolloff": 0.8,    # Target rolloff
                    "zero_crossing_rate": 0.1,  # Target zero crossing rate
                    "rms_energy": 0.5          # Target energy level
                }
                
                # Improve the model
                loss = self.improvement_model.improve(
                    current_state.features,
                    target_state
                )
                
                # Log improvement
                logging.info(f"Model improvement loss: {loss}")
                
                time.sleep(1)  # Update every second
            except Exception as e:
                logging.error(f"Error in improvement loop: {e}")
                time.sleep(5)  # Wait before retrying
                
    def _care_loop(self):
        while self.is_running:
            try:
                # Generate and execute care actions
                care_action = self.user_care.generate_care_action()
                if care_action != self.last_care_action:
                    self._execute_care_action(care_action)
                    self.last_care_action = care_action
                    
                    # Execute follow-up actions
                    if care_action.follow_up_actions:
                        for follow_up in care_action.follow_up_actions:
                            self._execute_follow_up_action(follow_up)
                            
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logging.error(f"Error in care loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    # Example usage
    interface = LivingInterface()
    
    try:
        interface.start()
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        logging.error(f"Error in main execution: {e}")
    finally:
        interface.stop() 