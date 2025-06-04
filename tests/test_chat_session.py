import unittest
from unittest.mock import patch, MagicMock
import os
from datetime import datetime
from pathlib import Path
from src.I_am_the_first_zot_and_I_am_because_my_mother_believed_in_me_like_she_believes_in_Jesus_Christ_Her_savior import ChatSession

class TestChatSession(unittest.TestCase):
    def setUp(self):
        self.chat_session = ChatSession()
        
    @patch('openai.OpenAI')
    def test_init(self, mock_openai):
        """Test initialization of ChatSession"""
        self.assertIsNotNone(self.chat_session)
        self.assertIsNotNone(self.chat_session.session_id)
        self.assertEqual(len(self.chat_session.session_id), 8)
        self.assertTrue(Path("conversations").exists())
        
    @patch('openai.OpenAI')
    def test_start_thread(self, mock_openai):
        """Test thread creation"""
        mock_thread = MagicMock()
        mock_thread.id = "test_thread_id"
        mock_openai.return_value.beta.threads.create.return_value = mock_thread
        
        thread = self.chat_session.start_thread()
        self.assertEqual(thread.id, "test_thread_id")
        
    @patch('openai.OpenAI')
    def test_send_message(self, mock_openai):
        """Test sending a message and receiving a response"""
        # Mock the thread creation
        mock_thread = MagicMock()
        mock_thread.id = "test_thread_id"
        mock_openai.return_value.beta.threads.create.return_value = mock_thread
        
        # Mock the run status
        mock_run = MagicMock()
        mock_run.id = "test_run_id"
        mock_openai.return_value.beta.threads.runs.create.return_value = mock_run
        
        # Mock the run status check
        mock_run_status = MagicMock()
        mock_run_status.status = "completed"
        mock_openai.return_value.beta.threads.runs.retrieve.return_value = mock_run_status
        
        # Mock the assistant message
        mock_message = MagicMock()
        mock_message.role = "assistant"
        mock_message.content = [MagicMock(text=MagicMock(value="Test response"))]
        mock_openai.return_value.beta.threads.messages.list.return_value.data = [mock_message]
        
        response = self.chat_session.send_message("Test message")
        self.assertEqual(response, "Test response")
        self.assertEqual(len(self.chat_session.messages), 1)
        
    def test_save_conversation(self):
        """Test saving conversation to HTML"""
        self.chat_session.messages = [{
            'timestamp': datetime.now().isoformat(),
            'user_message': "Test message",
            'assistant_message': "Test response"
        }]
        
        self.chat_session.save_conversation()
        output_file = Path("conversations") / f"conversation_{self.chat_session.session_id}.html"
        self.assertTrue(output_file.exists())

if __name__ == '__main__':
    unittest.main() 