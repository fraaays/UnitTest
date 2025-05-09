import unittest
from unittest.mock import MagicMock, patch
from Bot_client import (
    choose_difficulty, difficulty_range, guessing_loop,
    get_user_difficulty, connect_to_server, play_game
)
import socket

class TestGuessingGame(unittest.TestCase):

    def test_difficulty_range(self):
        self.assertEqual(difficulty_range("1"), (1, 40))
        self.assertEqual(difficulty_range("2"), (1, 75))
        self.assertEqual(difficulty_range("3"), (1, 100))
        self.assertEqual(difficulty_range("invalid"), (1, 100))  # fallback

    def test_choose_difficulty(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"Choose level", b"Ready to guess"]
        result = choose_difficulty(mock_socket, "1")
        self.assertEqual(result, (1, 40))
        mock_socket.sendall.assert_called_with(b"1\n")

    def test_guessing_loop_correct_guess(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"CORRECT!"]
        result = guessing_loop(mock_socket, 1, 100)
        self.assertEqual(result, 50)

    def test_guessing_loop_higher(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"Higher", b"CORRECT!"]
        result = guessing_loop(mock_socket, 1, 100)
        self.assertEqual(result, 75)

    def test_guessing_loop_lower(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"Lower", b"CORRECT!"]
        result = guessing_loop(mock_socket, 1, 100)
        self.assertEqual(result, 25)

    def test_guessing_loop_multiple_steps(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [
            b"Higher",    # guess = 50
            b"Higher",    # guess = 75
            b"Lower",     # guess = 88
            b"CORRECT!"   # guess = 81
        ]
        result = guessing_loop(mock_socket, 1, 100)
        self.assertEqual(result, 81)

    def test_get_user_difficulty(self):
        with patch("builtins.input", return_value="2"):
            self.assertEqual(get_user_difficulty(), "2")

    def test_connect_to_server(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket_instance = MagicMock()
            mock_socket_class.return_value = mock_socket_instance

            host = "localhost"
            port = 7777
            s = connect_to_server(host, port)
            mock_socket_instance.connect.assert_called_with((host, port))
            self.assertEqual(s, mock_socket_instance)

    def test_play_game(self):
        # Mock all components used in play_game()
        with patch("Bot_client.connect_to_server") as mock_connect, \
             patch("Bot_client.get_user_difficulty", return_value="1"), \
             patch("Bot_client.choose_difficulty", return_value=(1, 40)), \
             patch("Bot_client.guessing_loop", return_value=32):

            mock_socket = MagicMock()
            mock_connect.return_value = mock_socket

            result = play_game("localhost", 7777)
            self.assertEqual(result, 32)
            mock_socket.close.assert_called_once()

    # NEW TEST: Test invalid difficulty input (to cover the fallback in difficulty_range)
    def test_invalid_difficulty_input(self):
        mock_socket = MagicMock()
        mock_socket.recv.side_effect = [b"Choose level", b"Ready to guess"]
        # Test an invalid difficulty input to ensure fallback to (1, 100)
        result = choose_difficulty(mock_socket, "invalid")
        self.assertEqual(result, (1, 100))
        mock_socket.sendall.assert_called_with(b"invalid\n")

    # NEW TEST: Test socket connection failure or invalid server response (edge case)
    def test_connect_to_server_failure(self):
        with patch("socket.socket") as mock_socket_class:
            mock_socket_instance = MagicMock()
            mock_socket_class.return_value = mock_socket_instance
            mock_socket_instance.connect.side_effect = socket.error("Connection failed")
            with self.assertRaises(socket.error):
                connect_to_server("localhost", 7777)

if __name__ == '__main__':
    unittest.main()
