import os
import shutil
import tempfile
import re
from datetime import datetime
from system_monitor import SystemMonitor
import platform


class CommandHandler:
    def __init__(self):
        self.sandbox_dir = tempfile.mkdtemp(prefix='pyterminal_')
        self.current_dir = self.sandbox_dir
        self._populate_demo_environment()
        self.sysmon = SystemMonitor()

    def _populate_demo_environment(self):
        # Create demo folders and files
        os.makedirs(os.path.join(self.sandbox_dir, 'documents'), exist_ok=True)
        os.makedirs(os.path.join(self.sandbox_dir, 'projects'), exist_ok=True)
        os.makedirs(os.path.join(self.sandbox_dir, 'logs'), exist_ok=True)
        with open(os.path.join(self.sandbox_dir, 'documents', 'readme.txt'), 'w') as f:
            f.write(
                "Welcome to PyTerminal!\n"
                "\n"
                "Author: Agrasen Rai\n"
                "College: SRMIST\n"
                "Registration No.: RA2211003010604\n"
                "Mail: ar8546@srmist.edu.in\n"
                "\n"
                "Try these features:\n"
                "- Classic commands: ls, cd, mkdir, rm, cat, etc.\n"
                "- AI mode: natural language queries (\"create a folder called demo and move all .txt files into it\")\n"
                "- File explorer: click to preview files\n"
                "- Multi-terminal: open/switch/close tabs\n"
                "- System monitor: see CPU/memory below\n"
                "- Help: click ? for all commands\n"
                "\n"
            )

        with open(os.path.join(self.sandbox_dir, 'projects', 'example.py'), 'w') as f:
            f.write('# Example Python file\nprint("Hello, world!")')
        with open(os.path.join(self.sandbox_dir, 'logs', 'system.log'), 'w') as f:
            f.write('[INFO] System started at {}\n'.format(datetime.now()))
        with open(os.path.join(self.sandbox_dir, 'data.json'), 'w') as f:
            f.write('{"demo": true, "version": "1.0"}')
        with open(os.path.join(self.sandbox_dir, 'README.md'), 'w') as f:
            f.write('# PyTerminal Demo\n- Try commands like ls, cd, cat, mkdir, rm, sysinfo, top, etc.')

    def _safe_path(self, path):
        # Prevent path traversal outside sandbox
        abs_path = os.path.abspath(os.path.join(self.current_dir, path))
        sandbox_root = os.path.abspath(self.sandbox_dir)
        if not abs_path.startswith(sandbox_root):
            raise PermissionError(f'You can only access files and folders inside your sandbox ("~"). Current sandbox root: {sandbox_root}')
        return abs_path

    def execute(self, command, cwd=None):
        self.current_dir = cwd or self.sandbox_dir
        try:
            # Minimal support for 'ls -l | grep ...'
            if '|' in command:
                left, right = [x.strip() for x in command.split('|', 1)]
                if right.startswith('grep '):
                    pattern = right[5:].strip().strip('"\'')
                    left_output = self.execute(left, self.current_dir)
                    filtered = '\n'.join([line for line in left_output.split('\n') if pattern in line])
                    return filtered if filtered else '[No matches]'
                else:
                    return 'Only simple pipes with grep are supported (e.g., ls -l | grep pattern).'
            # Handle echo with > for file writing
            if command.strip().startswith('echo') and '>' in command:
                parts = command.split('>')
                left = parts[0].strip()
                right = parts[1].strip()
                text = left[5:].strip().strip('"\'')
                path = self._safe_path(right)
                with open(path, 'w') as f:
                    f.write(text + '\n')
                return f'Wrote to {right}'
            cmd, *args = re.split(r'\s+', command.strip(), maxsplit=1)
            arg = args[0] if args else ''
            # File/dir commands
            if cmd in ['ls', 'dir']:
                if '-l' in arg:
                    return self._ls_long(arg.replace('-l', '').strip())
                return self._ls(arg)
            elif cmd in ['cd']:
                return self._cd(arg)
            elif cmd in ['pwd']:
                return self._pwd()
            elif cmd in ['mkdir', 'md']:
                return self._mkdir(arg)
            elif cmd in ['touch']:
                return self._touch(arg)
            elif cmd in ['rm', 'del']:
                if '-r' in arg:
                    return self._rm(arg.replace('-r', '').strip(), recursive=True)
                return self._rm(arg)
            elif cmd in ['rmdir']:
                return self._rm(arg, recursive=True)
            elif cmd in ['cp', 'copy']:
                return self._cp(arg)
            elif cmd in ['mv', 'move']:
                return self._mv(arg)
            elif cmd in ['cat', 'type']:
                return self._cat(arg)
            elif cmd in ['head']:
                return self._head(arg)
            elif cmd in ['tail']:
                return self._tail(arg)
            elif cmd in ['wc']:
                return self._wc(arg)
            elif cmd in ['grep']:
                return self._grep(arg)
            elif cmd == 'find':
                return self._find(arg)
            elif cmd == 'tree':
                return self._tree(arg)
            elif cmd in ['nano', 'open']:
                return self._edit(arg)
            # System/user info
            elif cmd == 'whoami':
                return os.environ.get('USER', os.environ.get('USERNAME', 'user'))
            elif cmd == 'hostname':
                return platform.node()
            elif cmd == 'uname':
                if '-a' in arg:
                    return str(platform.uname())
                return platform.system()
            elif cmd == 'sw_vers':
                return 'ProductName: macOS\nProductVersion: Simulated\nBuildVersion: Simulated'
            elif cmd == 'systeminfo':
                return self.sysmon.sysinfo()
            elif cmd == 'df':
                if '-h' in arg:
                    return self.sysmon.df()
                return self.sysmon.df()
            elif cmd == 'free':
                if '-h' in arg:
                    return self.sysmon.free()
                return self.sysmon.free()
            elif cmd == 'echo':
                if '$PATH' in arg:
                    return os.environ.get('PATH', '')
                if '%PATH%' in arg:
                    return os.environ.get('PATH', '')
                return arg
            elif cmd == 'date':
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Process/monitoring
            elif cmd in ['ps']:
                if 'aux' in arg:
                    return self.sysmon.ps()
                return self.sysmon.ps()
            elif cmd == 'tasklist':
                return self.sysmon.ps()
            elif cmd == 'top':
                return self.sysmon.top()
            elif cmd == 'htop':
                return 'htop is not installed. Showing top instead.\n' + self.sysmon.top()
            elif cmd == 'kill':
                return self._kill(arg)
            elif cmd == 'taskkill':
                return self._taskkill(arg)
            # Network/system commands (simulated)
            elif cmd == 'ping':
                return f'Pinging {arg}...\nReply from 127.0.0.1: bytes=32 time<1ms TTL=64\nPing complete (simulated)'
            elif cmd == 'ifconfig':
                return 'eth0: inet 127.0.0.1 netmask 255.0.0.0 (simulated)'
            elif cmd == 'ip':
                if arg.strip() == 'a':
                    return '1: lo: <LOOPBACK> mtu 65536\n    inet 127.0.0.1/8 (simulated)'
                return 'Unknown ip command'
            elif cmd == 'ipconfig':
                return 'Ethernet adapter: IPv4 Address: 127.0.0.1 (simulated)'
            elif cmd == 'netstat':
                if '-an' in arg:
                    return 'Proto Local Address           Foreign Address         State\nTCP    0.0.0.0:80            0.0.0.0:0              LISTENING (simulated)'
                elif '-tulpn' in arg:
                    return 'Proto Local Address           PID/Program name\ntcp    0.0.0.0:80            1234/python (simulated)'
                return 'netstat output (simulated)'
            elif cmd == 'ss':
                if '-tulpn' in arg:
                    return 'Netid State      Local Address:Port  Peer Address:Port\ntcp   LISTEN     0.0.0.0:80         0.0.0.0:* (simulated)'
                return 'ss output (simulated)'
            elif cmd == 'Get-NetTCPConnection':
                return 'LocalAddress LocalPort RemoteAddress RemotePort State\n127.0.0.1   80        0.0.0.0        0         Listen (simulated)'
            elif cmd == 'lsof':
                return 'COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME\npython3  1234 user   3u  IPv4  12345      0t0  TCP *:80 (LISTEN) (simulated)'
            # Default
            elif cmd == 'welcome':
                return self._welcome()
            else:
                return f'Unknown command: {cmd}'
        except PermissionError as e:
            return f'Permission denied: {e}\nYou can only work inside your sandbox. Use relative paths or folders shown in the sidebar.'
        except FileNotFoundError as e:
            return f'File not found: {e}'
        except Exception as e:
            return f'Error: {e}'

    def _ls(self, arg):
        path = self._safe_path(arg or '.')
        if not os.path.exists(path):
            raise FileNotFoundError(arg)
        items = os.listdir(path)
        return '\n'.join(items) if items else '[Empty directory]'

    def _ls_long(self, arg):
        path = self._safe_path(arg or '.')
        if not os.path.exists(path):
            raise FileNotFoundError(arg)
        items = os.listdir(path)
        lines = []
        for item in items:
            full = os.path.join(path, item)
            stat = os.stat(full)
            size = stat.st_size
            mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
            typ = 'd' if os.path.isdir(full) else '-'
            lines.append(f'{typ} {size:>8} {mtime} {item}')
        return '\n'.join(lines) if lines else '[Empty directory]'

    def _cd(self, arg):
        if not arg:
            self.current_dir = self.sandbox_dir
            return self.current_dir
        path = self._safe_path(arg)
        if not os.path.isdir(path):
            raise FileNotFoundError(arg)
        self.current_dir = path
        return self.current_dir

    def _pwd(self):
        # Show current directory relative to sandbox
        rel = os.path.relpath(self.current_dir, self.sandbox_dir)
        return '~' if rel == '.' else f'~/{rel.replace(os.sep, "/")}'

    def _mkdir(self, arg):
        if not arg:
            return 'Usage: mkdir <folder>'
        # Remove -p if present (AI compatibility)
        parts = arg.split()
        if '-p' in parts:
            parts.remove('-p')
        folder = ' '.join(parts).strip()
        if not folder:
            return 'Usage: mkdir <folder>'
        path = self._safe_path(folder)
        os.makedirs(path, exist_ok=True)
        return f'Directory created: {folder}'

    def _rm(self, arg, recursive=False):
        if not arg:
            return 'Usage: rm <file|folder>'
        path = self._safe_path(arg)
        if os.path.isdir(path):
            if recursive:
                shutil.rmtree(path)
                return f'Directory deleted: {arg}'
            else:
                return 'Use rm -r or rmdir to delete a directory.'
        elif os.path.isfile(path):
            os.remove(path)
            return f'File deleted: {arg}'
        else:
            raise FileNotFoundError(arg)

    def _cp(self, arg):
        parts = arg.split()
        if not parts:
            return 'Usage: cp <src> <dst> or cp -r <src_dir> <dst_dir>'
        if parts[0] == '-r' and len(parts) == 3:
            src = self._safe_path(parts[1])
            dst = self._safe_path(parts[2])
            if not os.path.isdir(src):
                return 'Source must be a directory for cp -r.'
            if os.path.exists(dst):
                return 'Destination already exists.'
            try:
                import shutil
                shutil.copytree(src, dst)
                return f'Recursively copied {parts[1]} to {parts[2]}'
            except Exception as e:
                return f'Error copying directory: {e}'
        elif len(parts) == 2:
            src = self._safe_path(parts[0])
            dst = self._safe_path(parts[1])
            if os.path.isdir(src):
                return 'Use cp -r to copy directories.'
            import shutil
            shutil.copy2(src, dst)
            return f'Copied {parts[0]} to {parts[1]}'
        else:
            return 'Usage: cp <src> <dst> or cp -r <src_dir> <dst_dir>'

    def _mv(self, arg):
        parts = arg.split()
        if len(parts) != 2:
            return 'Usage: mv <src> <dst>'
        src = self._safe_path(parts[0])
        dst = self._safe_path(parts[1])
        shutil.move(src, dst)
        return f'Moved {parts[0]} to {parts[1]}'

    def _cat(self, arg):
        if not arg:
            return 'Usage: cat <file>'
        path = self._safe_path(arg)
        if not os.path.isfile(path):
            raise FileNotFoundError(arg)
        with open(path, 'r') as f:
            return f.read()

    def _edit(self, arg):
        if not arg:
            return 'Usage: nano <file>'
        path = self._safe_path(arg)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write('')
        with open(path, 'r') as f:
            content = f.read()
        return f'--- {arg} ---\n{content}\n[Editing not supported in web UI. Use cat/type to view.]'

    def _welcome(self):
        return 'Welcome to your sandboxed terminal. Type commands below.'

    def _kill(self, arg):
        try:
            pid = int(arg.strip())
            os.kill(pid, 9)
            return f'Process {pid} killed.'
        except Exception:
            return 'Invalid PID or insufficient permissions.'

    def _taskkill(self, arg):
        m = re.search(r'/PID\s+(\d+)', arg)
        if m:
            pid = int(m.group(1))
            try:
                os.kill(pid, 9)
                return f'Process {pid} killed.'
            except Exception:
                return 'Invalid PID or insufficient permissions.'
        return 'Usage: taskkill /PID <id> /F'

    def _touch(self, arg):
        if not arg:
            return 'Usage: touch <file>'
        path = self._safe_path(arg)
        with open(path, 'a'):
            os.utime(path, None)
        return f'File created: {arg}'

    def _head(self, arg):
        if not arg:
            return 'Usage: head <file>'
        path = self._safe_path(arg)
        if not os.path.isfile(path):
            raise FileNotFoundError(arg)
        with open(path, 'r') as f:
            lines = [next(f) for _ in range(10) if not f.tell() == os.fstat(f.fileno()).st_size]
        return ''.join(lines)

    def _tail(self, arg):
        if not arg:
            return 'Usage: tail <file>'
        path = self._safe_path(arg)
        if not os.path.isfile(path):
            raise FileNotFoundError(arg)
        with open(path, 'r') as f:
            lines = f.readlines()[-10:]
        return ''.join(lines)

    def _wc(self, arg):
        if not arg:
            return 'Usage: wc <file>'
        path = self._safe_path(arg)
        if not os.path.isfile(path):
            raise FileNotFoundError(arg)
        with open(path, 'r') as f:
            content = f.read()
        lines = content.count('\n')
        words = len(content.split())
        chars = len(content)
        return f'{lines} {words} {chars} {arg}'

    def _grep(self, arg):
        parts = arg.split()
        if len(parts) < 2:
            return 'Usage: grep <pattern> <file>'
        pattern, filename = parts[0], ' '.join(parts[1:])
        path = self._safe_path(filename)
        if not os.path.isfile(path):
            raise FileNotFoundError(filename)
        with open(path, 'r') as f:
            matches = [line for line in f if pattern in line]
        return ''.join(matches) if matches else '[No matches]'

    def _find(self, arg):
        if '-name' in arg:
            pattern = arg.split('-name', 1)[1].strip().strip('"\'')
            matches = []
            for root, dirs, files in os.walk(self.current_dir):
                for file in files:
                    if pattern in file:
                        matches.append(os.path.relpath(os.path.join(root, file), self.current_dir))
            return '\n'.join(matches) if matches else '[No matches]'
        return 'Usage: find . -name <pattern>'

    def _tree(self, arg):
        def walk(path, prefix=''):
            lines = []
            items = os.listdir(path)
            for i, item in enumerate(items):
                full = os.path.join(path, item)
                connector = '└── ' if i == len(items)-1 else '├── '
                lines.append(prefix + connector + item)
                if os.path.isdir(full):
                    extension = '    ' if i == len(items)-1 else '│   '
                    lines.extend(walk(full, prefix + extension))
            return lines
        path = self._safe_path(arg or '.')
        return '\n'.join(walk(path))
