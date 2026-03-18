document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('gc-api-key');
    const modelSelect = document.getElementById('gc-model');
    const memoryToggle = document.getElementById('gc-memory');
    const memoryLabel = document.getElementById('gc-memory-label');
    const newSessionBtn = document.getElementById('gc-new-session');
    const contextBtn = document.getElementById('gc-context-btn');
    const contextModal = document.getElementById('gc-context-modal');
    const contextClose = document.getElementById('gc-context-close');
    const contextContent = document.getElementById('gc-context-content');
    const chatArea = document.getElementById('gc-chat-area');
    const messageInput = document.getElementById('gc-message');
    const fileInput = document.getElementById('gc-file-input');
    const fileLabel = document.getElementById('gc-file-label');
    const sendBtn = document.getElementById('gc-send-btn');
    const loading = document.getElementById('gc-loading');
    const errorDiv = document.getElementById('gc-error');

    let sessionId = null;
    let selectedFiles = [];

    // Load models
    fetch('/api/gemini-chat/models')
        .then(r => r.json())
        .then(models => {
            modelSelect.innerHTML = '';
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = m.name;
                modelSelect.appendChild(opt);
            });
        });

    // New session
    async function createSession() {
        const r = await fetch('/api/gemini-chat/session/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ memory: memoryToggle.checked }),
        });
        const data = await r.json();
        sessionId = data.session_id;
        chatArea.innerHTML = '<p class="text-muted">New session started. Type a message below.</p>';
        errorDiv.classList.add('hidden');
    }

    newSessionBtn.addEventListener('click', createSession);

    // Memory toggle
    memoryToggle.addEventListener('change', async () => {
        memoryLabel.textContent = memoryToggle.checked ? 'Memory ON' : 'Memory OFF';
        if (sessionId) {
            await fetch('/api/gemini-chat/memory', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, memory: memoryToggle.checked }),
            });
        }
    });

    // File attachment
    fileInput.addEventListener('change', () => {
        selectedFiles = Array.from(fileInput.files);
        if (selectedFiles.length) {
            fileLabel.textContent = selectedFiles.map(f => f.name).join(', ');
            fileLabel.classList.remove('hidden');
        } else {
            fileLabel.classList.add('hidden');
        }
    });

    // View context window
    contextBtn.addEventListener('click', async () => {
        if (!sessionId) return;
        const r = await fetch(`/api/gemini-chat/context/${sessionId}`);
        const data = await r.json();
        if (!data.history || data.history.length === 0) {
            contextContent.textContent = '(empty context — no messages yet)';
        } else {
            let text = `Messages in context: ${data.message_count}\n\n`;
            data.history.forEach((msg, i) => {
                const role = msg.role === 'user' ? 'YOU' : 'GEMINI';
                const parts = msg.parts.map(p => p.text || '[file]').join('');
                text += `--- ${role} ---\n${parts}\n\n`;
            });
            contextContent.textContent = text;
        }
        contextModal.classList.remove('hidden');
        contextModal.style.display = 'flex';
    });

    contextClose.addEventListener('click', () => { contextModal.classList.add('hidden'); contextModal.style.display = ''; });
    contextModal.addEventListener('click', (e) => {
        if (e.target === contextModal) { contextModal.classList.add('hidden'); contextModal.style.display = ''; }
    });

    // Send message
    sendBtn.addEventListener('click', sendMessage);
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });

    async function sendMessage() {
        const msg = messageInput.value.trim();
        if (!msg) return;
        if (!apiKeyInput.value.trim()) {
            errorDiv.textContent = 'Please enter your Gemini API key';
            errorDiv.classList.remove('hidden');
            return;
        }
        errorDiv.classList.add('hidden');

        // Auto-create session if none
        if (!sessionId) await createSession();

        // Add user bubble
        appendBubble('user', msg, selectedFiles.map(f => f.name));

        const fd = new FormData();
        fd.append('api_key', apiKeyInput.value.trim());
        fd.append('model', modelSelect.value);
        fd.append('message', msg);
        fd.append('session_id', sessionId);
        selectedFiles.forEach(f => fd.append('files', f));

        messageInput.value = '';
        selectedFiles = [];
        fileInput.value = '';
        fileLabel.classList.add('hidden');
        loading.classList.remove('hidden');
        sendBtn.disabled = true;

        try {
            const r = await fetch('/api/gemini-chat/send', { method: 'POST', body: fd });
            const data = await r.json();
            if (data.error) throw new Error(data.error);
            appendBubble('model', data.text);
            if (data.usage) {
                appendUsage(data.usage);
            }
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
            sendBtn.disabled = false;
        }
    }

    function appendBubble(role, text, fileNames) {
        // Remove placeholder
        const placeholder = chatArea.querySelector('.text-muted');
        if (placeholder) placeholder.remove();

        const isUser = role === 'user';
        const bubble = document.createElement('div');
        bubble.style.cssText = `padding:0.75rem 1rem;margin-bottom:0.5rem;border-radius:8px;
            background:${isUser ? 'var(--accent-dim)' : 'var(--bg-tertiary)'};
            border-left:3px solid ${isUser ? 'var(--accent)' : 'var(--green)'};
            white-space:pre-wrap;word-wrap:break-word;font-size:0.88rem;`;

        const label = document.createElement('div');
        label.style.cssText = `font-size:0.75rem;font-weight:600;margin-bottom:0.3rem;color:${isUser ? 'var(--accent)' : 'var(--green)'};`;
        label.textContent = isUser ? 'You' : 'Gemini';
        bubble.appendChild(label);

        if (fileNames && fileNames.length) {
            const fileDiv = document.createElement('div');
            fileDiv.style.cssText = 'font-size:0.75rem;color:var(--text-muted);margin-bottom:0.3rem;';
            fileDiv.textContent = 'Files: ' + fileNames.join(', ');
            bubble.appendChild(fileDiv);
        }

        const textDiv = document.createElement('div');
        textDiv.textContent = text;
        bubble.appendChild(textDiv);
        chatArea.appendChild(bubble);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function appendUsage(usage) {
        const div = document.createElement('div');
        div.style.cssText = 'font-size:0.72rem;color:var(--text-muted);text-align:right;margin-bottom:0.5rem;';
        div.textContent = `Tokens: ${usage.prompt_tokens} in / ${usage.response_tokens} out / ${usage.total_tokens} total`;
        chatArea.appendChild(div);
    }
});
