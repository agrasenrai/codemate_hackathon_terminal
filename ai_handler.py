import re
from datetime import datetime

# --- Hackathon-winning: Regex-based AI, multi-phrase support, suggestions, logging ---

class AIHandler:
    def __init__(self):
        self.patterns = [
            (re.compile(r'create (?:a )?folder called (.+)', re.I), lambda m: f"mkdir {m.group(1)}"),
            (re.compile(r'list (?:all )?files', re.I), lambda m: "ls"),
            (re.compile(r'go to (.+) folder', re.I), lambda m: lambda x: f"cd {m.group(1)}"),
            (re.compile(r'show system information', re.I), lambda m: "sysinfo"),
            (re.compile(r'delete file called (.+)', re.I), lambda m: f"rm {m.group(1)}"),
            (re.compile(r'clear (?:the )?screen', re.I), lambda m: "clear"),
            (re.compile(r'show me what\'s running', re.I), lambda m: "top"),
            (re.compile(r'cat (.+)', re.I), lambda m: f"cat {m.group(1)}"),
            (re.compile(r'go to (.+)', re.I), lambda m: f"cd {m.group(1)}"),
        ]
        self.log = []

    def interpret(self, text):
        for pat, func in self.patterns:
            m = pat.match(text)
            if m:
                cmd = func(m)
                self.log.append({'input': text, 'command': cmd, 'time': datetime.now().isoformat()})
                return {'interpreted': True, 'command': cmd, 'input': text}
        # Suggestion for unclear input
        suggestion = self._suggest(text)
        self.log.append({'input': text, 'command': None, 'suggestion': suggestion, 'time': datetime.now().isoformat()})
        return {'interpreted': False, 'command': None, 'input': text, 'suggestion': suggestion}

    def _suggest(self, text):
        if 'folder' in text:
            return 'Try: mkdir <folder>'
        if 'file' in text:
            return 'Try: cat <file> or rm <file>'
        if 'system' in text:
            return 'Try: sysinfo or top'
        return 'Command not recognized. Try a basic command or see help.'
