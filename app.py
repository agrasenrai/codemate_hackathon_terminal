import os
import logging
from flask import Flask, render_template, request, jsonify, session, send_from_directory, abort
from commands import CommandHandler
from system_monitor import SystemMonitor
from ai_handler import AIHandler
from datetime import timedelta
from flask_cors import CORS


def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.secret_key = os.environ.get('SECRET_KEY', 'pyterminal-secret')
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    CORS(app)

    # Logging
    logging.basicConfig(level=logging.INFO)

    # Command, system, and AI handlers
    command_handler = CommandHandler()
    system_monitor = SystemMonitor()
    ai_handler = AIHandler()

    @app.route('/')
    def index():
        # Always start in sandbox for new session
        session['cwd'] = command_handler.sandbox_dir
        return render_template('index.html')

    @app.route('/execute', methods=['POST'])
    def execute():
        data = request.get_json()
        user_input = data.get('command', '')
        ai_mode = data.get('ai', False)
        print(f"[DEBUG] /execute called. AI mode: {ai_mode}, input: {user_input}")
        session.permanent = True
        if 'cwd' not in session or not session['cwd'].startswith(command_handler.sandbox_dir):
            session['cwd'] = command_handler.sandbox_dir
        cwd = session['cwd']
        if ai_mode:
            ai_result = ai_handler.interpret(user_input)
            print(f"[DEBUG] AIHandler result: {ai_result}")
            if ai_result['interpreted'] and 'commands' in ai_result:
                outputs = []
                for cmd in ai_result['commands']:
                    print(f"[DEBUG] Executing AI command: {cmd}")
                    out = command_handler.execute(cmd, cwd)
                    print(f"[DEBUG] Output: {out}")
                    outputs.append(f"$ {cmd}\n{out}")
                    session['cwd'] = command_handler.current_dir
                    cwd = session['cwd']
                ai_result['output'] = '\n\n'.join(outputs)
                return jsonify(ai_result)
            # AI failed to interpret
            output = command_handler.execute(user_input, cwd)
            print(f"[DEBUG] AI fallback output: {output}")
            session['cwd'] = command_handler.current_dir
            return jsonify({'interpreted': False, 'command': user_input, 'output': output})
        else:
            output = command_handler.execute(user_input, cwd)
            print(f"[DEBUG] Direct command output: {output}")
            session['cwd'] = command_handler.current_dir
            return jsonify({'interpreted': False, 'command': user_input, 'output': output})

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    @app.route('/filetree')
    def filetree():
        def build_tree(path):
            items = []
            for name in sorted(os.listdir(path)):
                full_path = os.path.join(path, name)
                if os.path.isdir(full_path):
                    items.append({
                        'name': name,
                        'type': 'dir',
                        'path': os.path.relpath(full_path, command_handler.sandbox_dir),
                        'children': build_tree(full_path)
                    })
                else:
                    items.append({
                        'name': name,
                        'type': 'file',
                        'path': os.path.relpath(full_path, command_handler.sandbox_dir)
                    })
            return items
        tree = build_tree(command_handler.sandbox_dir)
        return jsonify(tree)

    @app.route('/preview')
    def preview():
        rel_path = request.args.get('path', '')
        abs_path = os.path.abspath(os.path.join(command_handler.sandbox_dir, rel_path))
        if not abs_path.startswith(command_handler.sandbox_dir):
            abort(403)
        if not os.path.isfile(abs_path):
            abort(404)
        try:
            with open(abs_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read(2048)
            return content
        except Exception:
            return 'Unable to preview file.', 500

    @app.route('/ai_suggest', methods=['POST'])
    def ai_suggest():
        data = request.get_json()
        user_input = data.get('input', '')
        ai_result = ai_handler.interpret(user_input)
        print(f"[DEBUG] /ai_suggest input: {user_input}, ai_result: {ai_result}")
        suggestion = ''
        if ai_result.get('interpreted') and ai_result.get('commands'):
            suggestion = ai_result['commands'][0]
        return jsonify({'suggestion': suggestion})

    @app.route('/ai_prompt_suggest', methods=['POST'])
    def ai_prompt_suggest():
        data = request.get_json()
        user_input = data.get('input', '')
        suggestion = ai_handler.prompt_completion(user_input)
        print(f"[DEBUG] /ai_prompt_suggest input: {user_input}, suggestion: {suggestion}")
        return jsonify({'suggestion': suggestion})

    @app.route('/sysstats')
    def sysstats():
        stats = system_monitor.get_stats()
        return jsonify(stats)

    # Static file serving optimization
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
