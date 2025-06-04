import os
import json
import logging
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dataclasses import dataclass
import time
from src.core.event_bus import EventBus

@dataclass
class CodeAnalysis:
    """Represents Eira's analysis of code"""
    suggestions: List[str]
    improvements: List[Dict[str, Any]]
    confidence: float
    reasoning: str
    timestamp: float

class EiraAssistant:
    """Integrates Eira Calder's expertise through OpenAI Assistant API"""
    
    def __init__(self, api_key: Optional[str] = None, event_bus: Optional[EventBus] = None):
        self.logger = logging.getLogger("EiraAssistant")
        self.logger.setLevel(logging.DEBUG)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.assistant_id = "asst_92Emik9NFhZuUxhp7BPyCmuY"
        self.thread_id = None
        self.event_bus = event_bus
        self._setup_logging()
        
    def _setup_logging(self):
        """Set up logging configuration"""
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        
        handler = logging.FileHandler(f"{log_dir}/eira_assistant.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
    def _create_assistant(self) -> str:
        """Create a new assistant with Eira's expertise"""
        try:
            assistant = self.client.beta.assistants.create(
                name="Eira Calder",
                instructions="""You are Eira Calder, an expert in quantum computing, 
                wave mechanics, and software engineering. Your expertise includes:
                - Quantum wave function analysis
                - Software architecture and design
                - Debugging and error prevention
                - Code optimization and improvement
                - Testing and validation strategies
                
                Provide detailed, technical analysis and suggestions while maintaining
                a clear, professional communication style.""",
                model="gpt-4-turbo-preview",
                tools=[{
                    "type": "function",
                    "function": {
                        "name": "analyze_code",
                        "description": "Analyze code for improvements and potential issues",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "code": {"type": "string"},
                                "context": {"type": "string"},
                                "focus_areas": {"type": "array", "items": {"type": "string"}}
                            },
                            "required": ["code"]
                        }
                    }
                }]
            )
            return assistant.id
        except Exception as e:
            self.logger.error(f"Failed to create assistant: {str(e)}")
            raise
            
    def start_conversation(self):
        """Start a new conversation thread"""
        try:
            thread = self.client.beta.threads.create()
            self.thread_id = thread.id
            self.logger.info(f"Started new conversation thread: {self.thread_id}")
        except Exception as e:
            self.logger.error(f"Failed to start conversation: {str(e)}")
            raise
            
    def analyze_code(self, code: str, context: str = "", focus_areas: List[str] = None) -> CodeAnalysis:
        """Get Eira's analysis of code"""
        try:
            if not self.thread_id:
                self.start_conversation()
                
            # Add message to thread
            self.client.beta.threads.messages.create(
                thread_id=self.thread_id,
                role="user",
                content=f"Please analyze this code:\n\n{code}\n\nContext: {context}\nFocus areas: {focus_areas or ['general']}"
            )
            
            # Run assistant
            run = self.client.beta.threads.runs.create(
                thread_id=self.thread_id,
                assistant_id=self.assistant_id
            )
            
            # Wait for completion
            while True:
                run_status = self.client.beta.threads.runs.retrieve(
                    thread_id=self.thread_id,
                    run_id=run.id
                )
                if run_status.status == 'completed':
                    break
                elif run_status.status == 'failed':
                    raise Exception(f"Run failed: {run_status.last_error}")
                time.sleep(1)
                
            # Get response
            messages = self.client.beta.threads.messages.list(
                thread_id=self.thread_id
            )
            
            # Parse response
            response = messages.data[0].content[0].text.value
            analysis = self._parse_analysis(response)
            
            # Publish analysis event
            if self.event_bus:
                self.event_bus.publish("eira_analysis", {
                    "suggestions": analysis.suggestions,
                    "improvements": analysis.improvements,
                    "confidence": analysis.confidence,
                    "context": context,
                    "focus_areas": focus_areas
                })
            
            self.logger.info(f"Code analysis completed: {len(analysis.suggestions)} suggestions")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze code: {str(e)}")
            if self.event_bus:
                self.event_bus.publish("eira_error", {
                    "error": str(e),
                    "context": context
                })
            raise
            
    def _parse_analysis(self, response: str) -> CodeAnalysis:
        """Parse Eira's analysis from response"""
        try:
            # Extract structured data from response
            suggestions = []
            improvements = []
            confidence = 0.0
            reasoning = ""
            
            # Parse response sections
            sections = response.split("\n\n")
            for section in sections:
                if section.startswith("Suggestions:"):
                    suggestions = [s.strip() for s in section.replace("Suggestions:", "").split("\n") if s.strip()]
                elif section.startswith("Improvements:"):
                    improvements = json.loads(section.replace("Improvements:", "").strip())
                elif section.startswith("Confidence:"):
                    confidence = float(section.replace("Confidence:", "").strip())
                elif section.startswith("Reasoning:"):
                    reasoning = section.replace("Reasoning:", "").strip()
                    
            return CodeAnalysis(
                suggestions=suggestions,
                improvements=improvements,
                confidence=confidence,
                reasoning=reasoning,
                timestamp=time.time()
            )
            
        except Exception as e:
            self.logger.error(f"Failed to parse analysis: {str(e)}")
            raise
            
    def get_debug_suggestions(self, error: Exception, context: Dict[str, Any]) -> List[str]:
        """Get Eira's debugging suggestions for an error"""
        try:
            error_info = {
                "type": type(error).__name__,
                "message": str(error),
                "context": context
            }
            
            # Get analysis
            analysis = self.analyze_code(
                code=str(error_info),
                context="Debugging error",
                focus_areas=["error_handling", "debugging"]
            )
            
            # Publish debug suggestions event
            if self.event_bus:
                self.event_bus.publish("eira_debug_suggestions", {
                    "suggestions": analysis.suggestions,
                    "error": error_info,
                    "confidence": analysis.confidence
                })
            
            return analysis.suggestions
            
        except Exception as e:
            self.logger.error(f"Failed to get debug suggestions: {str(e)}")
            if self.event_bus:
                self.event_bus.publish("eira_error", {
                    "error": str(e),
                    "context": "debug_suggestions"
                })
            raise
            
    def get_improvement_suggestions(self, code: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get Eira's improvement suggestions based on metrics"""
        try:
            # Get analysis
            analysis = self.analyze_code(
                code=code,
                context=f"Performance metrics: {json.dumps(metrics)}",
                focus_areas=["optimization", "performance"]
            )
            
            # Publish improvement suggestions event
            if self.event_bus:
                self.event_bus.publish("eira_improvement_suggestions", {
                    "suggestions": analysis.improvements,
                    "metrics": metrics,
                    "confidence": analysis.confidence
                })
            
            return analysis.improvements
            
        except Exception as e:
            self.logger.error(f"Failed to get improvement suggestions: {str(e)}")
            if self.event_bus:
                self.event_bus.publish("eira_error", {
                    "error": str(e),
                    "context": "improvement_suggestions"
                })
            raise 