
const quotes = [
    '"AI is the new electricity." - Andrew Ng',
    '"Intelligence is the ability to adapt to change." - Stephen Hawking',
    '"Design is not just what it looks like and feels like. Design is how it works." - Steve Jobs'
];

function updateQuote() {
    const q = quotes[Math.floor(Math.random() * quotes.length)];
    const el = document.getElementById('daily-quote');
    if (el) el.textContent = q;
}
// Ultra State Management
let sessions = JSON.parse(localStorage.getItem('sessions')) || [{ id: 'default', title: 'Chat Utama', messages: [] }];
let currentSessionId = localStorage.getItem('currentSessionId') || 'default';
let imageHistory = JSON.parse(localStorage.getItem('imageHistory')) || [];
let isDarkMode = localStorage.getItem('darkMode') === 'true';
let customSystemPrompt = localStorage.getItem('customSystemPrompt') || "Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia. Gunakan format Markdown untuk jawaban yang panjang atau teknis.";
let learnedContent = "";

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    applyTheme();
    renderSessions();
    switchSession(currentSessionId);
    renderImageHistory();
    loadAPIKeys();

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

function updateChatUI() {
    const engine = document.getElementById('chat-engine').value;
    const model = document.getElementById('chat-model').value;
    const badge = document.getElementById('iq-badge');
    const modelSelect = document.getElementById('chat-model');

    if (engine === 'ultra' || model.startsWith('hazz-')) {
        badge.textContent = model === 'hazz-1-ultra' ? '300+ IQ' : 'Ultra';
        badge.style.background = '#6f42c1';
        badge.style.color = 'white';
    } else {
        badge.textContent = 'Standard';
        badge.style.background = '#ffc107';
        badge.style.color = '#000';
    }

    if (engine === 'ultra') {
        modelSelect.style.display = 'none';
    } else {
        modelSelect.style.display = 'block';
    }
}

async function sendMessage() {
    if (attachedFileContent) {
        const input = document.getElementById('user-input');
        input.value = input.value + attachedFileContent;
        clearFile();
    }
    const input = document.getElementById('chat-input');
    const text = input.value.trim();
    const model = document.getElementById('chat-model').value;
    const engine = document.getElementById('chat-engine').value;

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
            body: JSON.stringify({
                message: text,
                model,
                engine,
                system_prompt: customSystemPrompt,
                learning_content: learnedContent
            })
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

    // Extract Thought block if present
    let thoughtHtml = "";
    const thoughtMatch = text.match(/<thought>([\s\S]*?)<\/thought>/);
    if (thoughtMatch) {
        const thoughtContent = thoughtMatch[1].trim();
        thoughtHtml = `<div class="thought-container">
            <div class="thought-header" onclick="this.parentElement.classList.toggle('collapsed')">
                <i class="fas fa-brain"></i> Proses Berpikir Hazz-1
            </div>
            <div class="thought-body">${marked.parse(thoughtContent)}</div>
        </div>`;
        text = text.replace(/<thought>[\s\S]*?<\/thought>/, "");
    }

    const rawHtml = thoughtHtml + marked.parse(text);
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
        const text = btn.textContent.toLowerCase();
        if (text === 'chat' && tabId === 'chat-tab') btn.classList.add('active');
        if (text === 'gambar' && tabId === 'image-tab') btn.classList.add('active');
        if (text === 'developer' && tabId === 'dev-tab') btn.classList.add('active');
    });
}

// Developer API Management
async function loadAPIKeys() {
    const container = document.getElementById('keys-list');
    if (!container) return;

    try {
        const response = await fetch('/developer/keys');
        const keys = await response.json();

        container.innerHTML = '';
        if (Object.keys(keys).length === 0) {
            container.innerHTML = '<p>Belum ada API Key. Silakan buat di atas.</p>';
            return;
        }

        for (const [key, info] of Object.entries(keys)) {
            const div = document.createElement('div');
            div.className = 'key-item';
            div.style.cssText = 'background: var(--sidebar-bg); padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid var(--border);';
            div.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <strong>${info.name}</strong>
                    <button onclick="revokeKey('${key}')" style="background: #dc3545; padding: 5px 10px; font-size: 12px;">Revoke</button>
                </div>
                <div style="margin-top: 10px; display: flex; gap: 10px;">
                    <code style="flex: 1; background: rgba(0,0,0,0.1); padding: 5px; border-radius: 5px;">${key}</code>
                    <button onclick="navigator.clipboard.writeText('${key}')" title="Copy"><i class="far fa-copy"></i></button>
                </div>
            `;
            container.appendChild(div);
        }
    } catch (e) {
        container.innerHTML = '<p>Gagal memuat API Keys.</p>';
    }
}

async function generateAPIKey() {
    const nameInput = document.getElementById('key-name');
    const name = nameInput.value.trim() || 'New Key';

    try {
        const response = await fetch('/developer/keys/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        const data = await response.json();
        if (data.key) {
            nameInput.value = '';
            loadAPIKeys();
        }
    } catch (e) {
        alert('Gagal membuat API Key.');
    }
}

async function revokeKey(key) {
    if (!confirm('Hapus API Key ini? Aplikasi yang menggunakan key ini tidak akan bisa lagi mengakses API.')) return;

    try {
        await fetch('/developer/keys/revoke', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ key })
        });
        loadAPIKeys();
    } catch (e) {
        alert('Gagal menghapus API Key.');
    }
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

function openPersonalityLab() {
    document.getElementById('custom-system-prompt').value = customSystemPrompt;
    document.getElementById('personality-modal').style.display = 'block';
}

function savePersonality() {
    const prompt = document.getElementById('custom-system-prompt').value.trim();
    if (prompt) {
        customSystemPrompt = prompt;
        localStorage.setItem('customSystemPrompt', customSystemPrompt);
        alert('Identitas AI telah diperbarui!');
        closeModal('personality-modal');
    }
}

function resetPersonality() {
    if (confirm('Reset identitas ke pengaturan awal?')) {
        customSystemPrompt = "Kamu adalah AI asisten yang pintar dan membantu. Jawablah dalam bahasa Indonesia. Gunakan format Markdown untuk jawaban yang panjang atau teknis.";
        localStorage.removeItem('customSystemPrompt');
        document.getElementById('custom-system-prompt').value = customSystemPrompt;
    }
}

function openLearningLab() {
    document.getElementById('learning-data').value = learnedContent;
    document.getElementById('learning-modal').style.display = 'block';
}

function saveLearningData() {
    const data = document.getElementById('learning-data').value.trim();
    learnedContent = data;
    if (data) {
        alert('AI telah menyerap materi baru!');
        closeModal('learning-modal');
    }
}

window.onclick = function(event) {
    if (event.target.className === 'modal') {
        event.target.style.display = "none";
    }
}

let attachedFileContent = "";

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    const btn = document.querySelector('label[for="file-upload"] i');
    btn.className = "fas fa-spinner fa-spin";

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.text) {
            attachedFileContent = `\n[DOKUMEN TERLAMPIR: ${data.filename}]\n${data.text}\n`;
            document.getElementById('file-preview').style.display = 'flex';
            document.getElementById('filename-display').textContent = data.filename;
        }
    } catch (err) {
        alert("Gagal mengunggah file.");
    } finally {
        btn.className = "fas fa-paperclip";
    }
}

function clearFile() {
    attachedFileContent = "";
    document.getElementById('file-upload').value = "";
    document.getElementById('file-preview').style.display = 'none';
}

async function updateChatTitle(id, message) {
    try {
        const response = await fetch('/generate-title', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ message })
        });
        const data = await response.json();
        const chat = chatSessions.find(s => s.id === id);
        if (chat && data.title) {
            chat.name = data.title;
            saveSessions();
            renderSessions();
        }
    } catch (e) {}
}

function useTool(type) {
    showTab('chat');
    let prompt = "";
    switch(type) {
        case 'translate': prompt = "Terjemahkan teks berikut ke Bahasa Indonesia: "; break;
        case 'summarize': prompt = "Buatkan ringkasan poin-poin penting dari teks ini: "; break;
        case 'code': prompt = "Rapikan dan jelaskan kode berikut: "; break;
        case 'math': prompt = "Selesaikan persoalan matematika ini langkah demi langkah: "; break;
        case 'email': prompt = "Tuliskan email profesional tentang: "; break;
        case 'social': prompt = "Buatkan caption sosial media yang menarik untuk: "; break;
        case 'grammar': prompt = "Perbaiki tata bahasa dan ejaan teks ini agar lebih natural: "; break;
        case 'keyword': prompt = "Berikan daftar keyword SEO yang relevan untuk topik: "; break;
        case 'idea': prompt = "Berikan 10 ide kreatif dan unik tentang: "; break;
        case 'job': prompt = "Buatkan draf surat lamaran kerja (Cover Letter) untuk posisi: "; break;
        case 'study': prompt = "Buatkan jadwal belajar efektif selama 1 minggu untuk subjek: "; break;
        case 'diet': prompt = "Buatkan menu makanan sehat harian untuk tujuan: "; break;

    }
    document.getElementById('user-input').value = prompt;
    document.getElementById('user-input').focus();
}

function setSpecialTheme(theme) {
    document.body.className = theme === 'default' ? '' : 'theme-' + theme;
    localStorage.setItem('hazz-special-theme', theme);
}

// Load saved theme
const savedSpecialTheme = localStorage.getItem('hazz-special-theme');
if (savedSpecialTheme) setSpecialTheme(savedSpecialTheme);

function exportChat() {
    if (!currentSession) return;
    let text = `# Chat: ${currentSession.name}\n\n`;
    currentSession.messages.forEach(m => {
        text += `**${m.role.toUpperCase()}**: ${m.content}\n\n---\n\n`;
    });

    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chat-${currentSession.name.toLowerCase().replace(/ /g, '-')}.md`;
    a.click();
}
