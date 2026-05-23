// Ultra State Management
let sessions = JSON.parse(localStorage.getItem('sessions')) || [{ id: 'default', title: 'Chat Utama', messages: [] }];
let currentSessionId = localStorage.getItem('currentSessionId') || 'default';
let imageHistory = JSON.parse(localStorage.getItem('imageHistory')) || [];
let isDarkMode = localStorage.getItem('darkMode') === 'true';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    renderSessions();
    switchSession(currentSessionId);
    renderImageHistory();

    // Auto-resize textarea
    const textarea = document.getElementById('chat-input');
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

function applyTheme() {
    document.body.classList.toggle('dark-mode', isDarkMode);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    localStorage.setItem('darkMode', isDarkMode);
    applyTheme();
}

function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
}

// Session Management
function renderSessions() {
    const container = document.getElementById('chat-sessions');
    container.innerHTML = '';
    sessions.forEach(session => {
        const div = document.createElement('div');
        div.className = `chat-session-item ${session.id === currentSessionId ? 'active' : ''}`;
        div.innerHTML = `
            <span><i class="far fa-comment"></i> ${session.title}</span>
            <i class="fas fa-times delete-session" onclick="deleteSession('${session.id}', event)"></i>
        `;
        div.onclick = () => switchSession(session.id);
        container.appendChild(div);
    });
}

function createNewChat() {
    const id = 'session-' + Date.now();
    const newSession = { id, title: 'Chat Baru', messages: [] };
    sessions.unshift(newSession);
    localStorage.setItem('sessions', JSON.stringify(sessions));
    switchSession(id);
    renderSessions();
}

function switchSession(id) {
    currentSessionId = id;
    localStorage.setItem('currentSessionId', id);
    const session = sessions.find(s => s.id === id) || sessions[0];
    currentSessionId = session.id;

    renderSessions();
    const chatBox = document.getElementById('chat-messages');
    chatBox.innerHTML = '';

    if (session.messages.length === 0) {
        appendMessage('bot', 'Halo! Ini adalah ruang chat baru. Ada yang bisa saya bantu?');
    } else {
        session.messages.forEach(msg => appendMessage(msg.sender, msg.text, null, false));
    }

    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('open');
    }
}

function deleteSession(id, event) {
    event.stopPropagation();
    if (sessions.length <= 1) return;
    sessions = sessions.filter(s => s.id !== id);
    if (currentSessionId === id) {
        currentSessionId = sessions[0].id;
    }
    localStorage.setItem('sessions', JSON.stringify(sessions));
    localStorage.setItem('currentSessionId', currentSessionId);
    renderSessions();
    switchSession(currentSessionId);
}

// Chat Functionality
function handleChatKey(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    const model = document.getElementById('chat-model').value;

    if (!text) return;

    appendMessage('user', text);
    saveToCurrentSession('user', text);
    input.value = '';
    input.style.height = 'auto';

    const loaderId = 'loader-' + Date.now();
    appendMessage('bot', '<div class="loader"></div>', loaderId);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, model })
        });

        const data = await response.json();
        const loader = document.getElementById(loaderId);

        if (data.response) {
            loader.innerHTML = formatMarkdown(data.response);
            saveToCurrentSession('bot', data.response);
            updateSessionTitle(text);
        } else {
            loader.textContent = 'Maaf, terjadi kesalahan.';
        }
    } catch (e) {
        const loader = document.getElementById(loaderId);
        loader.textContent = 'Gagal terhubung ke server.';
    }

    const chatBox = document.getElementById('chat-messages');
    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(sender, text, id = null, animate = true) {
    const chatBox = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    if (id) div.id = id;

    if (sender === 'bot') {
        div.innerHTML = formatMarkdown(text);
    } else {
        div.textContent = text;
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;

    if (sender === 'bot' && animate && !text.includes('loader')) {
        // Simple typing effect could be added here
    }
}

function formatMarkdown(text) {
    if (text.includes('loader')) return text;
    const rawHtml = marked.parse(text);
    const cleanHtml = DOMPurify.sanitize(rawHtml);

    // Process code blocks for copy button and highlighting
    const temp = document.createElement('div');
    temp.innerHTML = cleanHtml;
    temp.querySelectorAll('pre code').forEach((block) => {
        hljs.highlightElement(block);
        const pre = block.parentElement;
        pre.style.position = 'relative';
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.innerHTML = '<i class="far fa-copy"></i>';
        btn.onclick = () => {
            navigator.clipboard.writeText(block.textContent);
            btn.innerHTML = '<i class="fas fa-check"></i>';
            setTimeout(() => btn.innerHTML = '<i class="far fa-copy"></i>', 2000);
        };
        pre.appendChild(btn);
    });

    return temp.innerHTML;
}

function saveToCurrentSession(sender, text) {
    const session = sessions.find(s => s.id === currentSessionId);
    if (session) {
        session.messages.push({ sender, text });
        localStorage.setItem('sessions', JSON.stringify(sessions));
    }
}

function updateSessionTitle(text) {
    const session = sessions.find(s => s.id === currentSessionId);
    if (session && session.title === 'Chat Baru') {
        session.title = text.substring(0, 20) + (text.length > 20 ? '...' : '');
        localStorage.setItem('sessions', JSON.stringify(sessions));
        renderSessions();
    }
}

function clearCurrentChat() {
    if (confirm('Hapus semua pesan di chat ini?')) {
        const session = sessions.find(s => s.id === currentSessionId);
        if (session) {
            session.messages = [];
            localStorage.setItem('sessions', JSON.stringify(sessions));
            switchSession(currentSessionId);
        }
    }
}

// Voice Features
function startSTT() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert('Browser Anda tidak mendukung Speech Recognition.');
        return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = 'id-ID';

    const btn = document.querySelector('.chat-actions button i.fa-microphone').parentElement;
    btn.style.color = 'red';

    recognition.onresult = (event) => {
        const text = event.results[0][0].transcript;
        document.getElementById('chat-input').value = text;
        btn.style.color = '';
    };

    recognition.onerror = () => {
        btn.style.color = '';
    };

    recognition.start();
}

function speak(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'id-ID';
    window.speechSynthesis.speak(utterance);
}

// Image Generator
async function generateImage() {
    const promptInput = document.getElementById('image-prompt');
    const prompt = promptInput.value.trim();
    const model = document.getElementById('image-model').value;
    const ratio = document.getElementById('image-ratio').value.split('x');

    if (!prompt) return;

    const resultDiv = document.getElementById('image-result');
    resultDiv.innerHTML = '<div class="loader"></div>';

    try {
        const seed = Math.floor(Math.random() * 1000000);
        const response = await fetch('/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, model, width: ratio[0], height: ratio[1], seed })
        });

        const data = await response.json();
        if (data.image_url) {
            const url = data.image_url;
            resultDiv.innerHTML = `<img src="${url}" alt="${prompt}" onclick="window.open('${url}', '_blank')">`;
            addToImageHistory(url, prompt);
        } else {
            resultDiv.innerHTML = '<p>Gagal membuat gambar.</p>';
        }
    } catch (e) {
        resultDiv.innerHTML = '<p>Kesalahan koneksi.</p>';
    }
}

function addToImageHistory(url, prompt) {
    imageHistory.unshift({ url, prompt });
    if (imageHistory.length > 20) imageHistory.pop();
    localStorage.setItem('imageHistory', JSON.stringify(imageHistory));
    renderImageHistory();
}

function renderImageHistory() {
    const container = document.getElementById('image-history');
    if (!container) return;
    container.innerHTML = '';
    imageHistory.forEach(item => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `<img src="${item.url}" title="${item.prompt}">`;
        div.onclick = () => {
            document.getElementById('image-result').innerHTML = `<img src="${item.url}" alt="${item.prompt}" onclick="window.open('${item.url}', '_blank')">`;
            document.getElementById('image-prompt').value = item.prompt;
        };
        container.appendChild(div);
    });
}

// Tab Management
function openTab(tabId) {
    const contents = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tabs .tab-btn');

    contents.forEach(content => content.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    // Set active button
    buttons.forEach(btn => {
        if (btn.textContent.toLowerCase() === (tabId === 'chat-tab' ? 'chat' : 'gambar')) {
            btn.classList.add('active');
        }
    });
}

// Modal Management
function openPromptLibrary() {
    document.getElementById('prompt-modal').style.display = 'block';
}

function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

function usePrompt(text) {
    document.getElementById('chat-input').value = text;
    closeModal('prompt-modal');
    document.getElementById('chat-input').focus();
    // trigger auto-resize
    document.getElementById('chat-input').dispatchEvent(new Event('input'));
}

window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = "none";
    }
}
