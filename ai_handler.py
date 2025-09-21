import re
import requests
import os
from datetime import datetime

# Gemini API Key (replace with your own or use env var)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

# List of supported commands for context
SUPPORTED_COMMANDS = [
    'pwd', 'cd', 'ls', 'ls -l', 'dir', 'mkdir', 'md', 'touch', 'echo', 'echo >', 'rm', 'del', 'rm -r', 'rmdir',
    'cp', 'copy', 'mv', 'move', 'cat', 'type', 'head', 'tail', 'wc', 'grep', 'find', 'tree', 'nano', 'open',
    'whoami', 'hostname', 'uname -a', 'sw_vers', 'systeminfo', 'df -h', 'free -h', 'date', 'clear',
    'ps aux', 'tasklist', 'top', 'htop', 'kill', 'taskkill', 'ping', 'ifconfig', 'ip a', 'ipconfig',
    'netstat -an', 'netstat -tulpn', 'ss -tulpn', 'Get-NetTCPConnection', 'lsof'
]

class AIHandler:
    def __init__(self):
        self.log = []

    def interpret(self, text):
        # Compose prompt for Gemini
        prompt = (
            "You are an AI assistant for a web-based terminal. "
            "Convert the following user request into one or more valid shell commands, using only the following supported commands: "
            f"{', '.join(SUPPORTED_COMMANDS)}. "
            "If the request is ambiguous, make a best guess. If it cannot be done, reply with an empty string. "
            "Only output the command(s), one per line, no explanation.\n"
            f"User request: {text}"
        )
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ]
        }
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': GEMINI_API_KEY
        }
        debug_info = {'prompt': prompt, 'payload': payload, 'headers': headers}
        print(f"[AIHandler] [DEBUG] Gemini API call: {debug_info}")
        try:
            resp = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=15)
            print(f"[AIHandler] [DEBUG] Gemini API response status: {resp.status_code}")
            print(f"[AIHandler] [DEBUG] Gemini API response text: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            # Parse Gemini response for commands
            commands = []
            try:
                parts = data['candidates'][0]['content']['parts']
                for part in parts:
                    lines = part.get('text', '').strip().split('\n')
                    for line in lines:
                        if line.strip():
                            commands.append(line.strip())
            except Exception as e:
                print(f"[AIHandler] [ERROR] Failed to parse Gemini response: {e}")
            self.log.append({'input': text, 'commands': commands, 'raw': data, 'time': datetime.now().isoformat()})
            if commands:
                return {'interpreted': True, 'commands': commands, 'input': text}
            else:
                return {'interpreted': False, 'commands': [], 'input': text, 'suggestion': 'Could not interpret command.'}
        except Exception as e:
            print(f"[AIHandler] [ERROR] Gemini API call failed: {e}")
            self.log.append({'input': text, 'error': str(e), 'time': datetime.now().isoformat()})
            return {'interpreted': False, 'commands': [], 'input': text, 'suggestion': f'AI error: {e}'}
