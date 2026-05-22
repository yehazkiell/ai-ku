// State Management
let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];
let isDarkMode = localStorage.getItem('darkMode') === 'true';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (isDarkMode) {
        document.body.classList.add('dark-mode');
        document.querySelector('#theme-toggle i').className = 'fas fa-sun';
    }
    loadHistory();
});

function openTab(tabId) {
    const contents = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');

    contents.forEach(content => content.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    // Find button that has the onclick with tabId
    buttons.forEach(btn => {
        if (btn.getAttribute('onclick').includes(tabId)) {
            btn.classList.add('active');
        }
    });
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode');
    const icon = document.querySelector('#theme-toggle i');
    icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
    localStorage.setItem('darkMode', isDarkMode);
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    const model = document.getElementById('chat-model').value;

    if (!message) return;

    appendMessage('user', message);
    saveMessage('user', message);
    input.value = '';

    const chatBox = document.getElementById('chat-messages');
    const loaderId = 'loader-' + Date.now();
    appendMessage('bot', '<div class="loader"></div>', loaderId);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, model })
        });

        const data = await response.json();
        const loader = document.getElementById(loaderId);

        if (data.response) {
            const formatted = formatMarkdown(data.response);
            loader.innerHTML = formatted;
            saveMessage('bot', data.response);
        } else {
            loader.textContent = 'Error: ' + (data.error || 'Unknown error');
        }
    } catch (error) {
        const loader = document.getElementById(loaderId);
        loader.textContent = 'Gagal menghubungi server.';
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(sender, text, id = null) {
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
}

function formatMarkdown(text) {
    if (text.includes('loader')) return text; // Don't format loader
    // Use marked and DOMPurify for safe rendering
    const rawHtml = marked.parse(text);
    return DOMPurify.sanitize(rawHtml);
}

function saveMessage(sender, text) {
    chatHistory.push({ sender, text });
    if (chatHistory.length > 50) chatHistory.shift(); // Keep last 50
    localStorage.setItem('chatHistory', JSON.stringify(chatHistory));
}

function loadHistory() {
    if (chatHistory.length > 0) {
        const chatBox = document.getElementById('chat-messages');
        chatBox.innerHTML = '';
        chatHistory.forEach(msg => {
            appendMessage(msg.sender, msg.text);
        });
    }
}

function clearChat() {
    if (confirm('Bersihkan semua riwayat chat?')) {
        chatHistory = [];
        localStorage.removeItem('chatHistory');
        document.getElementById('chat-messages').innerHTML = '<div class="message bot">Riwayat dibersihkan. Ada lagi yang bisa saya bantu?</div>';
    }
}

async function generateImage() {
    const promptInput = document.getElementById('image-prompt');
    const prompt = promptInput.value.trim();
    const model = document.getElementById('image-model').value;
    const ratio = document.getElementById('image-ratio').value.split('x');

    if (!prompt) return;

    const resultDiv = document.getElementById('image-result');
    const actionDiv = document.getElementById('image-actions');

    resultDiv.innerHTML = '<div class="loader"></div>';
    actionDiv.style.display = 'none';

    try {
        const seed = Math.floor(Math.random() * 1000000);
        const response = await fetch('/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt,
                model,
                width: ratio[0],
                height: ratio[1],
                seed
            })
        });

        const data = await response.json();
        if (data.image_url) {
            resultDiv.innerHTML = `<img id="generated-img" src="${data.image_url}" alt="${prompt}">`;
            actionDiv.style.display = 'flex';
        } else {
            resultDiv.innerHTML = '<p>Gagal membuat gambar.</p>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<p>Terjadi kesalahan koneksi.</p>';
    }
}

async function downloadImage() {
    const img = document.getElementById('generated-img');
    if (!img) return;

    try {
        const response = await fetch(img.src);
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai-ku-${Date.now()}.jpg`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (e) {
        // Fallback to opening in new tab if blob fails
        window.open(img.src, '_blank');
    }
}
