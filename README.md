# PyTerminal: AI-Powered VS Code-Style Web Terminal

**Author:** Agrasen Rai  
**College:** SRMIST  
**Registration No.:** RA2211003010604  
**Mail ID:** ar8546@srmist.edu.in

---

Terminal and sandbox enviroment live link : https://codemate-hackathon-terminal.onrender.com/;

## 🚀 Project Overview
PyTerminal is a full-stack, production-ready, AI-powered web terminal. It is designed for demos, and real-world use, with a focus on extensibility, security, and a beautiful user experience.

---


### 1. **Terminal UI**
- Merged input/output: commands and results appear in a single scrollable area.
- Sticky prompt at the bottom, just like VS Code.
- Modern dark theme, rounded corners, subtle shadows, and responsive design.
- Multi-terminal support: open, switch, and close multiple terminals (tab bar with “+” button).
- Auto-scroll to bottom after every command.

### 2. **Command Execution & History**
- All classic shell commands supported: `ls`, `cd`, `pwd`, `mkdir`, `rm`, `cat`, `cp`, `mv`, `grep`, `find`, `tree`, etc.
- Command history navigation with up/down arrows, persistent across sessions.
- Inline autocompletion for commands and files, with best-match logic (case-insensitive, partial match, sorted by relevance).
- Tab to accept suggestion (full prompt in AI mode, segment in classic mode).

### 3. **AI-Powered Natural Language Terminal**
- Toggle AI mode ON/OFF (sticky button at right of prompt).
- When AI is ON:
  - Copilot-style inline prompt suggestions as you type (from Gemini API).
  - Enter natural language queries (e.g., “create a folder called test and move all .txt files into it”).
  - Gemini interprets and returns only supported commands (pipes, code blocks, and unsupported flags are filtered out).
  - Minimal support for `ls -l | grep ...` (runs left command, filters with grep).
- When AI is OFF:
  - Classic command templates and file suggestions only.

### 4. **File Explorer & Preview**
- Sidebar file explorer with collapsible folders, click to preview any file.
- Tabbed file preview (like VS Code), open multiple files at once.
- File tree auto-refreshes after every command.

### 5. **System Monitor Bar**
- Live CPU and memory usage bar below the terminal, updates every 2 seconds.

### 6. **Sandboxed, Safe Environment**
- All file operations are restricted to a secure sandbox (no path traversal).
- Demo environment pre-populated with folders and files for instant use.

### 7. **Production-Ready Backend**
- Flask app with session support, CORS, error logging, and health check endpoint.
- Gunicorn/Render/Railway deployment ready (Procfile, requirements.txt, runtime.txt included).
- All commands and AI features are robustly error-handled.

### 8. **Other Details**
- Help modal (top right “?”) with all supported commands and usage.
- Keyboard shortcuts: Ctrl+L (clear), Ctrl+C (interrupt), Tab (autocomplete), Up/Down (history).
- Mobile responsive, touch-friendly.
- All user state (AI mode, history, terminals) is persistent.

