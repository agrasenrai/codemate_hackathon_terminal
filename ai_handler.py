import re
import requests
import os
from datetime import datetime

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'AIzaSyBIJg61XLCup4_yGOqO2NT6aYtdrCFiZxA')
GEMINI_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

SUPPORTED_COMMANDS = [
    'pwd', 'cd', 'ls', 'ls -l', 'dir', 'mkdir', 'md', 'touch', 'echo', 'echo >', 'rm', 'del', 'rm -r', 'rmdir',
    'cp', 'copy', 'mv', 'move', 'cat', 'type', 'head', 'tail', 'wc', 'grep', 'find', 'tree', 'nano', 'open',
    'whoami', 'hostname', 'uname -a', 'sw_vers', 'systeminfo', 'df -h', 'free -h', 'date', 'clear',
    'ps aux', 'tasklist', 'top', 'htop', 'kill', 'taskkill', 'ping', 'ifconfig', 'ip a', 'ipconfig',
    'netstat -an', 'netstat -tulpn', 'ss -tulpn', 'Get-NetTCPConnection', 'lsof'
]
FORBIDDEN = ['|', '&&', ';', '`', '$(', '```']

class AIHandler:
    def __init__(self):
        self.log = []

    def interpret(self, text):
        # Compose prompt for Gemini
        prompt = (
            "You are an AI assistant for a web-based terminal. "
            "Convert the following user request into one or more valid shell commands, using only the following supported commands: "
            f"{', '.join(SUPPORTED_COMMANDS)}. "
            "Do NOT use pipes (|), code blocks, triple backticks, or unsupported flags. "
            "Only output the command(s), one per line, no explanation, no code block formatting.\n"
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
            commands = []
            try:
                parts = data['candidates'][0]['content']['parts']
                for part in parts:
                    lines = part.get('text', '').strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue
                        if any(f in line for f in FORBIDDEN):
                            print(f"[AIHandler] [WARN] Forbidden shell construct in: {line}")
                            continue
                        if not any(line.startswith(cmd.split()[0]) for cmd in SUPPORTED_COMMANDS):
                            print(f"[AIHandler] [WARN] Unsupported command: {line}")
                            continue
                        commands.append(line)
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

    def prompt_completion(self, text):
        prompt = (
            "You are an AI assistant for a web-based terminal. "
            "Given a partial user request, suggest a likely full natural language prompt the user might want to type. "
            "Do not output shell commands, only complete the user's natural language prompt. "
            "If the input is already a full prompt, return it as is.\n"
            f"User input: {text}"
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
        print(f"[AIHandler] [DEBUG] Gemini prompt completion call: {{'prompt': prompt, 'payload': payload}}")
        try:
            resp = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=15)
            print(f"[AIHandler] [DEBUG] Gemini prompt completion response status: {resp.status_code}")
            print(f"[AIHandler] [DEBUG] Gemini prompt completion response text: {resp.text}")
            resp.raise_for_status()
            data = resp.json()
            suggestion = ''
            try:
                parts = data['candidates'][0]['content']['parts']
                for part in parts:
                    text = part.get('text', '').strip()
                    if text:
                        suggestion = text
                        break
            except Exception as e:
                print(f"[AIHandler] [ERROR] Failed to parse Gemini prompt completion: {e}")
            return suggestion
        except Exception as e:
            print(f"[AIHandler] [ERROR] Gemini prompt completion call failed: {e}")
            return ''
