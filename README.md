# PyTerminal: AI-Powered Web Terminal

## Overview
PyTerminal is a production-ready, web-based Python terminal with AI-powered natural language command interpretation. Designed for hackathons, education, and demos, it features a professional terminal UI, real-time system monitoring, and safe sandboxed command execution.

## Features
- Realistic terminal UI (green/blue/amber themes, animations, mobile support)
- AI natural language command processor (regex-based)
- Safe file system operations in a sandbox
- System monitoring (CPU, memory, disk, processes)
- Command history, autocomplete, keyboard shortcuts
- Multi-user session support
- Production deployment (Railway/Render, Gunicorn)

## Quick Start
1. Clone repo and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run locally:
   ```bash
   flask run
   ```
3. Deploy to Railway/Render (Procfile/runtime.txt included)

## Demo Script
1. Open the live URL. Admire the animated ASCII art and welcome message.
2. Try basic commands: `ls`, `cd documents`, `cat readme.txt`, `mkdir demo`.
3. Use AI: Type "show me all files", "create folder called demo", "go to projects".
4. Run system commands: `sysinfo`, `top`, `ps`, `df`, `free`.
5. Showcase error handling: invalid commands, permission denied, file not found.
6. Switch themes, use keyboard shortcuts (Ctrl+L, Ctrl+C), and demo mobile view.

## Hackathon-Winning Highlights
- Stunning, animated terminal UI with pro polish
- AI-powered command interpretation (regex, suggestions, logging)
- Real system monitoring and safe sandboxed execution
- Cross-platform, production-ready, and extensible
- Comprehensive error handling and demo environment

## File Structure
- `app.py` - Flask app and API
- `commands.py` - CommandHandler (file ops, sandbox)
- `system_monitor.py` - System stats and monitoring
- `ai_handler.py` - AI natural language processor
- `static/` - CSS, JS, images
- `templates/` - HTML (Jinja2)

## License
MIT
