// Hackathon-winning: Real-time terminal UI, history, autocomplete, themes, typing effect, mobile support
let history = [];
let historyIdx = -1;
let executedCommands = [];
let openTabs = [];
let activeTab = null;

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
}

function handleInput(e) {
  const input = document.getElementById('terminal-input');
  if (e.key === 'Enter') {
    const cmd = input.value.trim();
    if (!cmd) return;
    history.push(cmd);
    historyIdx = history.length;
    addOutput(document.querySelector('.terminal-prompt').textContent + ' ' + cmd);
    executedCommands.push(cmd);
    input.value = '';
    fetch('/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: cmd })
    })
    .then(res => res.json())
    .then(data => {
      if (data.output) addOutput(data.output);
      else if (data.suggestion) addOutput('[AI Suggestion] ' + data.suggestion);
      // Update cwd in prompt if present in output
      fetchCwd();
      fetchFileTree(); // Refresh sidebar after every command
    });
  } else if (e.key === 'ArrowUp') {
    if (historyIdx > 0) {
      historyIdx--;
      input.value = history[historyIdx];
    }
    e.preventDefault();
  } else if (e.key === 'ArrowDown') {
    if (historyIdx < history.length - 1) {
      historyIdx++;
      input.value = history[historyIdx];
    } else {
      input.value = '';
      historyIdx = history.length;
    }
    e.preventDefault();
  } else if (e.ctrlKey && e.key.toLowerCase() === 'l') {
    addOutput('[[CLEAR]]');
    input.value = '';
    e.preventDefault();
  } else if (e.ctrlKey && e.key.toLowerCase() === 'c') {
    addOutput('^C');
    input.value = '';
    e.preventDefault();
  }
}

function fetchCwd() {
  fetch('/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ command: 'pwd' })
  })
  .then(res => res.json())
  .then(data => {
    if (data.output) {
      document.getElementById('cwd').textContent = data.output;
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

document.addEventListener('DOMContentLoaded', () => {
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
});
