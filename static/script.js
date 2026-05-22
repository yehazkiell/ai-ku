function openTab(tabId) {
    const contents = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');

    contents.forEach(content => content.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));

    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    appendMessage('user', message);
    input.value = '';

    const chatBox = document.getElementById('chat-messages');
    const loaderId = 'loader-' + Date.now();
    appendMessage('bot', '<div class="loader"></div>', loaderId);

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        const loader = document.getElementById(loaderId);

        if (data.response) {
            loader.textContent = '';
            loader.appendChild(document.createTextNode(data.response));
            // Basic new line formatting
            loader.style.whiteSpace = 'pre-wrap';
        } else {
            loader.textContent = 'Maaf, terjadi kesalahan: ' + (data.error || 'Unknown error');
        }
    } catch (error) {
        const loader = document.getElementById(loaderId);
        loader.textContent = 'Maaf, gagal menghubungi server.';
    }

    chatBox.scrollTop = chatBox.scrollHeight;
}

function appendMessage(sender, text, id = null) {
    const chatBox = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    if (id) div.id = id;

    if (text.includes('<div class="loader"></div>')) {
        div.innerHTML = text;
    } else {
        div.textContent = text;
        div.style.whiteSpace = 'pre-wrap';
    }

    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function generateImage() {
    const promptInput = document.getElementById('image-prompt');
    const prompt = promptInput.value.trim();
    if (!prompt) return;

    const resultDiv = document.getElementById('image-result');
    resultDiv.innerHTML = '<div class="loader"></div>';

    try {
        const seed = Math.floor(Math.random() * 1000000);
        const response = await fetch('/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, seed })
        });

        const data = await response.json();
        if (data.image_url) {
            resultDiv.innerHTML = `<img src="${data.image_url}" alt="${prompt}" onload="this.style.opacity=1" style="opacity:0; transition: opacity 0.5s;">`;
        } else {
            resultDiv.innerHTML = '<p>Gagal membuat gambar.</p>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<p>Terjadi kesalahan koneksi.</p>';
    }
}
