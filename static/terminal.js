// Hackathon-winning: Real-time terminal UI, history, autocomplete, themes, typing effect, mobile support
let history = [];
let historyIdx = -1;
let executedCommands = [];
let openTabs = [];
let activeTab = null;
let aiMode = false;
let inlineSuggestion = '';
let aiSuggestTimeout = null;
let lastAiSuggestInput = '';
let lastAiSuggestResult = '';
let aiPromptSuggestTimeout = null;
let lastAiPromptSuggestInput = '';
let lastAiPromptSuggestResult = '';
let lastAiPromptRequestId = 0;
let terminals = [createTerminalSession()];
let activeTerminal = 0;
let lastCwdForFiles = '';
let cachedFiles = [];

function createTerminalSession() {
  return {
    history: [],
    historyIdx: 0,
    executedCommands: [],
    cwd: '~',
    aiMode: aiMode,
    input: '',
  };
}

function renderTerminalTabs() {
  const tabs = document.getElementById('terminal-tabs');
  tabs.innerHTML = '';
  terminals.forEach((term, idx) => {
    const tab = document.createElement('div');
    tab.className = 'terminal-tab' + (idx === activeTerminal ? ' active' : '');
    tab.dataset.term = idx;
    tab.textContent = `Terminal ${idx + 1} `;
    const closeBtn = document.createElement('span');
    closeBtn.className = 'close-term';
    closeBtn.title = 'Close';
    closeBtn.textContent = '×';
    closeBtn.onclick = (e) => {
      e.stopPropagation();
      closeTerminal(idx);
    };
    tab.appendChild(closeBtn);
    tab.onclick = () => switchTerminal(idx);
    tabs.appendChild(tab);
  });
  const newBtn = document.createElement('button');
  newBtn.id = 'new-terminal-btn';
  newBtn.className = 'new-terminal-btn';
  newBtn.title = 'New Terminal';
  newBtn.textContent = '+';
  newBtn.onclick = () => {
    terminals.push(createTerminalSession());
    activeTerminal = terminals.length - 1;
    renderTerminalTabs();
    renderTerminalSession();
  };
  tabs.appendChild(newBtn);
}

function switchTerminal(idx) {
  if (idx < 0 || idx >= terminals.length) return;
  saveActiveTerminalState();
  activeTerminal = idx;
  renderTerminalTabs();
  renderTerminalSession();
}

function closeTerminal(idx) {
  if (terminals.length === 1) return; // Always keep at least one terminal
  terminals.splice(idx, 1);
  if (activeTerminal >= terminals.length) activeTerminal = terminals.length - 1;
  renderTerminalTabs();
  renderTerminalSession();
}

function saveActiveTerminalState() {
  const term = terminals[activeTerminal];
  term.aiMode = aiMode;
  term.input = document.getElementById('terminal-input').value;
  // Save history, cwd, etc. as needed
}

function renderTerminalSession() {
  const term = terminals[activeTerminal];
  aiMode = term.aiMode;
  setAiMode(aiMode);
  // Render history/output
  const body = document.getElementById('terminal-body');
  body.innerHTML = '';
  term.executedCommands.forEach(line => {
    const output = document.createElement('div');
    output.className = 'terminal-output';
    output.textContent = line;
    body.appendChild(output);
  });
  // Set input value
  document.getElementById('terminal-input').value = term.input || '';
  // Set cwd
  document.getElementById('cwd').textContent = term.cwd;
  // Set focus
  document.getElementById('terminal-input').focus();
  // Scroll to bottom
  setTimeout(() => {
    body.scrollTop = body.scrollHeight;
  }, 0);
}

function addOutput(text) {
  const output = document.createElement('div');
  output.className = 'terminal-output';
  if (text === '[[CLEAR]]') {
    document.getElementById('terminal-body').innerHTML = '';
    return;
  }
  output.textContent = text;
  document.getElementById('terminal-body').appendChild(output);
  document.getElementById('terminal-body').scrollTop = document.getElementById('terminal-body').scrollHeight;
  terminals[activeTerminal].executedCommands.push(text);
}

function setAiMode(on) {
  aiMode = on;
  const btn = document.getElementById('ai-toggle');
  if (aiMode) {
    btn.classList.add('active');
    btn.textContent = 'AI ON';
  } else {
    btn.classList.remove('active');
    btn.textContent = 'AI OFF';
  }
  localStorage.setItem('aiMode', aiMode ? '1' : '0');
  terminals[activeTerminal].aiMode = on;
}

function saveHistory() {
  localStorage.setItem('cmdHistory', JSON.stringify(history));
}
function loadHistory() {
  const h = localStorage.getItem('cmdHistory');
  if (h) history = JSON.parse(h);
  else history = [];
  historyIdx = history.length;
}

const SUGGESTION_TEMPLATES = [
  'pwd',
  'cd <folder>',
  'ls',
  'ls -l',
  'dir',
  'mkdir <folder_name>',
  'md <folder_name>',
  'touch <file>',
  'echo "<text>" > <file>',
  'rm <file>',
  'del <file>',
  'rm -r <folder>',
  'rmdir <folder>',
  'cp <src> <dst>',
  'copy <src> <dst>',
  'mv <src> <dst>',
  'move <src> <dst>',
  'cat <file>',
  'type <file>',
  'head <file>',
  'tail <file>',
  'wc <file>',
  'grep <pattern> <file>',
  'find . -name <pattern>',
  'tree',
  'nano <file>',
  'open <file>',
  'whoami',
  'hostname',
  'uname -a',
  'sw_vers',
  'systeminfo',
  'df -h',
  'free -h',
  'date',
  'clear',
  'ps aux',
  'tasklist',
  'top',
  'htop',
  'kill <pid>',
  'taskkill /PID <id> /F',
  'ping <host>',
  'ifconfig',
  'ip a',
  'ipconfig',
  'netstat -an',
  'netstat -tulpn',
  'ss -tulpn',
  'Get-NetTCPConnection',
  'lsof'
];

function getCurrentDirFiles(cb) {
  const cwd = document.getElementById('cwd').textContent.replace(/^~\/?/, '');
  if (cwd === lastCwdForFiles && cachedFiles.length) {
    cb(cachedFiles);
    return;
  }
  fetch('/filetree').then(res => res.json()).then(tree => {
    function findDir(node, path) {
      if (path === '' || path === '.') return node;
      const parts = path.split('/');
      let curr = node;
      for (let part of parts) {
        if (!part) continue;
        curr = (curr.find(n => n.name === part && n.type === 'dir') || {}).children || [];
      }
      return curr;
    }
    const files = findDir(tree, cwd).map(f => f.name);
    lastCwdForFiles = cwd;
    cachedFiles = files;
    cb(files);
  });
}

function bestStaticSuggestion(val, templates, files) {
  val = val.toLowerCase();
  let all = templates.concat(files);
  // Prioritize: startsWith > contains > no match
  let starts = all.filter(c => c.toLowerCase().startsWith(val));
  if (starts.length) return starts[0];
  let contains = all.filter(c => c.toLowerCase().includes(val));
  if (contains.length) return contains[0];
  return '';
}

function aiSuggest(input, cb) {
  if (!input.trim()) return cb('');
  fetch('/ai_suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input })
  })
    .then(res => res.json())
    .then(data => {
      cb(data.suggestion || '');
    })
    .catch(() => cb(''));
}

function aiPromptSuggest(input, cb) {
  if (!input.trim()) return cb('');
  const requestId = ++lastAiPromptRequestId;
  fetch('/ai_prompt_suggest', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input })
  })
    .then(res => res.json())
    .then(data => {
      // Only show if this is the latest request
      if (requestId === lastAiPromptRequestId) {
        cb(data.suggestion || '');
      }
    })
    .catch(() => {
      if (requestId === lastAiPromptRequestId) cb('');
    });
}

function showInlineAutocomplete(suggestion) {
  const input = document.getElementById('terminal-input');
  let ghost = document.getElementById('inline-autocomplete');
  if (!ghost) {
    ghost = document.createElement('span');
    ghost.id = 'inline-autocomplete';
    ghost.style.position = 'absolute';
    ghost.style.pointerEvents = 'none';
    ghost.style.color = '#b5cea888';
    ghost.style.fontFamily = 'inherit';
    ghost.style.fontSize = '1em';
    ghost.style.fontStyle = 'italic';
    ghost.style.userSelect = 'none';
    ghost.style.left = '0';
    ghost.style.top = '0';
    ghost.style.whiteSpace = 'pre';
    ghost.style.zIndex = '10';
    input.parentNode.appendChild(ghost);
  }
  const val = input.value;
  // Only show if cursor is at end
  if (input.selectionStart !== val.length || !val) {
    ghost.textContent = '';
    ghost.style.display = 'none';
    inlineSuggestion = '';
    return;
  }
  if (suggestion && suggestion !== val && suggestion.startsWith(val)) {
    // Use a hidden span to measure the width of the input value for precise left offset
    let measurer = document.getElementById('input-width-measurer');
    if (!measurer) {
      measurer = document.createElement('span');
      measurer.id = 'input-width-measurer';
      measurer.style.visibility = 'hidden';
      measurer.style.position = 'absolute';
      measurer.style.whiteSpace = 'pre';
      measurer.style.fontFamily = 'inherit';
      measurer.style.fontSize = '1em';
      measurer.style.fontStyle = 'inherit';
      input.parentNode.appendChild(measurer);
    }
    measurer.textContent = val;
    const offset = measurer.offsetWidth;
    ghost.textContent = suggestion.slice(val.length);
    ghost.style.display = 'inline';
    ghost.style.left = offset + 'px';
    inlineSuggestion = suggestion;
  } else {
    ghost.textContent = '';
    ghost.style.display = 'none';
    inlineSuggestion = '';
  }
}

function acceptNextSegment() {
  const input = document.getElementById('terminal-input');
  if (aiMode && inlineSuggestion) {
    input.value = inlineSuggestion;
    hideInlineAutocomplete();
    return;
  }
  if (!inlineSuggestion || !inlineSuggestion.startsWith(input.value)) return;
  const val = input.value;
  const rest = inlineSuggestion.slice(val.length);
  // Find next space or end
  let nextSpace = rest.indexOf(' ');
  if (nextSpace === -1) {
    input.value = inlineSuggestion;
  } else {
    input.value = val + rest.slice(0, nextSpace + 1);
  }
  // Move cursor to end
  input.setSelectionRange(input.value.length, input.value.length);
  // Update suggestion
  getCurrentDirFiles(files => {
    const all = SUGGESTION_TEMPLATES.concat(files);
    const suggestion = all.find(c => c.startsWith(input.value) && c !== input.value);
    showInlineAutocomplete(suggestion);
  });
}

function hideInlineAutocomplete() {
  let ghost = document.getElementById('inline-autocomplete');
  if (ghost) ghost.style.display = 'none';
  inlineSuggestion = '';
}

function handleInput(e) {
  const term = terminals[activeTerminal];
  aiMode = term.aiMode;
  const input = document.getElementById('terminal-input');
  if (e.key === 'Enter') {
    hideInlineAutocomplete();
    const cmd = input.value.trim();
    if (!cmd) return;
    term.history.push(cmd);
    saveHistory();
    term.historyIdx = term.history.length;
    addOutput(document.querySelector('.terminal-prompt').textContent + ' ' + cmd);
    input.value = '';
    fetch('/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: cmd, ai: aiMode })
    })
    .then(res => res.json())
    .then(data => {
      if (data.output) addOutput(data.output);
      else if (data.suggestion) addOutput('[AI Suggestion] ' + data.suggestion);
      fetchCwd();
      fetchFileTree();
    });
  } else if (e.key === 'ArrowUp') {
    hideInlineAutocomplete();
    if (term.historyIdx > 0) {
      term.historyIdx--;
      input.value = term.history[term.historyIdx];
    }
    e.preventDefault();
  } else if (e.key === 'ArrowDown') {
    hideInlineAutocomplete();
    if (term.historyIdx < term.history.length - 1) {
      term.historyIdx++;
      input.value = term.history[term.historyIdx];
    } else {
      input.value = '';
      term.historyIdx = term.history.length;
    }
    e.preventDefault();
  } else if (e.ctrlKey && e.key.toLowerCase() === 'l') {
    hideInlineAutocomplete();
    addOutput('[[CLEAR]]');
    input.value = '';
    e.preventDefault();
  } else if (e.ctrlKey && e.key.toLowerCase() === 'c') {
    hideInlineAutocomplete();
    addOutput('^C');
    input.value = '';
    e.preventDefault();
  } else if (e.key === 'Tab') {
    // Accept next segment of suggestion
    acceptNextSegment();
    e.preventDefault();
  } else if (e.key === 'Escape') {
    hideInlineAutocomplete();
  } else {
    // Show inline autocomplete as user types
    const val = input.value;
    if (aiMode) {
      if (aiPromptSuggestTimeout) clearTimeout(aiPromptSuggestTimeout);
      aiPromptSuggestTimeout = setTimeout(() => {
        if (lastAiPromptSuggestInput === val) {
          showInlineAutocomplete(lastAiPromptSuggestResult);
          return;
        }
        aiPromptSuggest(val, suggestion => {
          lastAiPromptSuggestInput = val;
          lastAiPromptSuggestResult = suggestion;
          showInlineAutocomplete(suggestion);
        });
      }, 800);
    } else {
      getCurrentDirFiles(files => {
        const suggestion = bestStaticSuggestion(val, SUGGESTION_TEMPLATES, files);
        showInlineAutocomplete(suggestion);
      });
    }
  }
  // Save input value
  term.input = input.value;
};

function fetchCwd() {
  fetch('/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: 'pwd', ai: aiMode })
  })
  .then(res => res.json())
  .then(data => {
    if (data.output) {
      document.getElementById('cwd').textContent = data.output;
      terminals[activeTerminal].cwd = data.output;
    }
  });
}

function fetchFileTree() {
  fetch('/filetree')
    .then(res => res.json())
    .then(data => {
      renderFileTree(data, document.getElementById('file-tree'), true);
    });
}

function renderFileTree(tree, parent, collapsed = true) {
  parent.innerHTML = '';
  tree.forEach(item => {
    const li = document.createElement('li');
    li.textContent = item.name;
    if (item.type === 'dir') {
      li.classList.add('dir', 'collapsed');
      li.onclick = (e) => {
        e.stopPropagation();
        if (li.classList.contains('collapsed')) {
          li.classList.remove('collapsed');
          li.querySelector('ul').style.display = 'block';
        } else {
          li.classList.add('collapsed');
          li.querySelector('ul').style.display = 'none';
        }
      };
      const ul = document.createElement('ul');
      ul.style.marginLeft = '10px';
      ul.style.display = collapsed ? 'none' : 'block';
      renderFileTree(item.children, ul, true);
      li.appendChild(ul);
    } else {
      li.onclick = (e) => {
        e.stopPropagation();
        openFileTab(item);
      };
    }
    parent.appendChild(li);
  });
}

function openFileTab(item) {
  // Check if already open
  let tab = openTabs.find(t => t.path === item.path);
  if (!tab) {
    tab = { name: item.name, path: item.path };
    openTabs.push(tab);
    renderTabs();
  }
  setActiveTab(tab.path);
  fetch('/preview?path=' + encodeURIComponent(item.path))
    .then(res => res.text())
    .then(text => {
      document.getElementById('file-preview').textContent = text;
    });
}

function renderTabs() {
  const bar = document.getElementById('tab-bar');
  bar.innerHTML = '';
  openTabs.forEach(tab => {
    const tabEl = document.createElement('div');
    tabEl.className = 'vscode-tab' + (activeTab === tab.path ? ' active' : '');
    tabEl.textContent = tab.name;
    tabEl.onclick = () => setActiveTab(tab.path);
    const closeBtn = document.createElement('span');
    closeBtn.className = 'close-btn';
    closeBtn.textContent = '×';
    closeBtn.onclick = (e) => {
      e.stopPropagation();
      closeTab(tab.path);
    };
    tabEl.appendChild(closeBtn);
    bar.appendChild(tabEl);
  });
}

function setActiveTab(path) {
  activeTab = path;
  renderTabs();
  const tab = openTabs.find(t => t.path === path);
  if (tab) {
    fetch('/preview?path=' + encodeURIComponent(tab.path))
      .then(res => res.text())
      .then(text => {
        document.getElementById('file-preview').textContent = text;
      });
  }
}

function closeTab(path) {
  const idx = openTabs.findIndex(t => t.path === path);
  if (idx !== -1) {
    openTabs.splice(idx, 1);
    if (activeTab === path) {
      if (openTabs.length > 0) {
        setActiveTab(openTabs[openTabs.length - 1].path);
      } else {
        activeTab = null;
        document.getElementById('file-preview').textContent = '';
        renderTabs();
      }
    } else {
      renderTabs();
    }
  }
}

// System monitor polling
function pollSysStats() {
  fetch('/sysstats').then(res => res.json()).then(stats => {
    document.getElementById('sys-cpu').textContent = stats.cpu + '%';
    document.getElementById('sys-mem').textContent = stats.mem + '%';
  });
  setTimeout(pollSysStats, 2000);
}

document.addEventListener('DOMContentLoaded', () => {
  loadHistory();
  document.getElementById('terminal-input').addEventListener('keydown', handleInput);
  document.getElementById('terminal-input').focus();
  fetchFileTree();
  fetchCwd();
  // Welcome message
  fetch('/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: 'welcome' })
  })
  .then(res => res.json())
  .then(data => {
    if (data.output) addOutput(data.output);
  });

  // Help modal logic
  const helpBtn = document.getElementById('help-btn');
  const helpModal = document.getElementById('help-modal');
  const closeHelp = document.getElementById('close-help');
  helpBtn.onclick = () => { helpModal.style.display = 'flex'; };
  closeHelp.onclick = () => { helpModal.style.display = 'none'; };
  window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') helpModal.style.display = 'none';
  });

  // AI toggle logic
  const aiBtn = document.getElementById('ai-toggle');
  aiBtn.onclick = () => setAiMode(!aiMode);
  // Restore AI mode from localStorage
  setAiMode(localStorage.getItem('aiMode') === '1');
  renderTerminalTabs();
  renderTerminalSession();
  pollSysStats();

  // Auto-open documents/readme.txt on load
  setTimeout(() => {
    openFileTab({ name: 'readme.txt', path: 'documents/readme.txt' });
  }, 1000);
});
