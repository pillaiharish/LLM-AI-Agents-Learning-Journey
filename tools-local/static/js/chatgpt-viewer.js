document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('cg-search');
    const reprocessBtn = document.getElementById('cg-reprocess-btn');
    const convList = document.getElementById('cg-conv-list');
    const chatArea = document.getElementById('cg-chat-area');
    const exportArea = document.getElementById('cg-export-area');
    const loading = document.getElementById('cg-loading');
    const errorDiv = document.getElementById('cg-error');

    let conversations = [];
    let currentConvId = null;
    let searchTimeout = null;

    async function loadConversations() {
        loading.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        try {
            const r = await fetch('/api/chatgpt-viewer/conversations');
            if (!r.ok) throw new Error('Failed to load conversations');
            conversations = await r.json();
            renderList(conversations);
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    }

    function renderList(convs) {
        convList.innerHTML = '';
        if (!convs.length) {
            convList.innerHTML = '<p class="text-muted" style="padding:0.5rem;">No conversations found</p>';
            return;
        }
        convs.forEach(c => {
            const div = document.createElement('div');
            div.style.cssText = 'padding:0.5rem 0.75rem;cursor:pointer;border-bottom:1px solid var(--border);border-radius:4px;';
            div.innerHTML = `<div style="font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${c.title || 'Untitled'}</div>
                <div class="text-muted" style="font-size:0.75rem;">${c.message_count || 0} messages &middot; ${c.create_time || ''}</div>`;
            div.addEventListener('click', () => loadConversation(c.id));
            div.addEventListener('mouseenter', () => div.style.background = 'var(--accent-dim)');
            div.addEventListener('mouseleave', () => div.style.background = '');
            convList.appendChild(div);
        });
    }

    async function loadConversation(id) {
        currentConvId = id;
        loading.classList.remove('hidden');
        try {
            const r = await fetch(`/api/chatgpt-viewer/conversation/${id}`);
            if (!r.ok) throw new Error('Failed to load conversation');
            const data = await r.json();
            renderChat(data);
            exportArea.classList.remove('hidden');
        } catch (err) {
            chatArea.innerHTML = `<p class="text-red">${err.message}</p>`;
        } finally {
            loading.classList.add('hidden');
        }
    }

    function renderChat(data) {
        chatArea.innerHTML = `<h3 style="margin-bottom:1rem;font-size:1.1rem;">${data.title || 'Untitled'}</h3>`;
        const q = searchInput.value.trim().toLowerCase();
        (data.messages || []).forEach(m => {
            const isUser = m.role === 'user';
            const bubble = document.createElement('div');
            bubble.style.cssText = `padding:0.75rem 1rem;margin-bottom:0.5rem;border-radius:8px;
                background:${isUser ? 'var(--accent-dim)' : 'var(--bg-tertiary)'};
                border-left:3px solid ${isUser ? 'var(--accent)' : 'var(--green)'};
                white-space:pre-wrap;word-wrap:break-word;font-size:0.88rem;`;
            const label = document.createElement('div');
            label.style.cssText = `font-size:0.75rem;font-weight:600;margin-bottom:0.3rem;color:${isUser ? 'var(--accent)' : 'var(--green)'};`;
            label.textContent = isUser ? 'You' : 'ChatGPT';
            bubble.appendChild(label);

            let content = m.content || '';
            if (q && content.toLowerCase().includes(q)) {
                const regex = new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
                content = content.replace(regex, '<mark style="background:var(--accent);color:#1e1e1e;padding:0 2px;border-radius:2px;">$1</mark>');
            }
            const textDiv = document.createElement('div');
            textDiv.innerHTML = content;
            bubble.appendChild(textDiv);
            chatArea.appendChild(bubble);
        });
    }

    // Search
    searchInput.addEventListener('input', () => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(async () => {
            const q = searchInput.value.trim();
            if (!q) { renderList(conversations); return; }
            try {
                const r = await fetch(`/api/chatgpt-viewer/search?q=${encodeURIComponent(q)}`);
                const results = await r.json();
                renderList(results);
            } catch { /* ignore */ }
        }, 300);
    });

    // Export
    exportArea.querySelectorAll('button[data-format]').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!currentConvId) return;
            const fmt = btn.dataset.format;
            const r = await fetch(`/api/chatgpt-viewer/export/${currentConvId}?format=${fmt}`);
            const blob = await r.blob();
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = `conversation.${fmt}`;
            a.click();
        });
    });

    // Reprocess
    reprocessBtn.addEventListener('click', async () => {
        loading.classList.remove('hidden');
        await fetch('/api/chatgpt-viewer/reprocess', { method: 'POST' });
        await loadConversations();
    });

    loadConversations();
});
