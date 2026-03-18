document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('tc-text-input');
    const fileInput = document.getElementById('tc-file-input');
    const dropZone = document.getElementById('tc-drop-zone');
    const fileInfo = document.getElementById('tc-file-info');
    const modelSelect = document.getElementById('tc-model-select');
    const calculateBtn = document.getElementById('tc-calculate-btn');
    const resultsSection = document.getElementById('tc-results');
    const resultsMeta = document.getElementById('tc-results-meta');
    const resultsBody = document.getElementById('tc-results-body');
    const loading = document.getElementById('tc-loading');
    const errorMsg = document.getElementById('tc-error');

    let selectedFile = null;
    let activeTab = 'tc-text';

    // Tabs
    document.querySelectorAll('#page-token-calculator .tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('#page-token-calculator .tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#page-token-calculator .tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            activeTab = tab.dataset.tab;
            document.getElementById(`tab-${activeTab}`).classList.add('active');
        });
    });

    // Live stats
    textInput.addEventListener('input', () => {
        const text = textInput.value;
        const chars = text.length;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const est = Math.max(0, Math.round(words * 1.3));
        document.getElementById('tc-stat-chars').textContent = `${chars.toLocaleString()} characters`;
        document.getElementById('tc-stat-words').textContent = `${words.toLocaleString()} words`;
        document.getElementById('tc-stat-tokens').textContent = `${est.toLocaleString()} est. tokens`;
    });

    // File upload
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault(); dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) setFile(fileInput.files[0]); });

    function setFile(file) {
        selectedFile = file;
        fileInfo.textContent = `Selected: ${file.name} (${(file.size/1024).toFixed(1)} KB)`;
        fileInfo.classList.remove('hidden');
    }

    // Load models
    fetch('/api/token-calculator/models')
        .then(r => r.json())
        .then(models => {
            models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = `${m.name} (${m.provider})`;
                modelSelect.appendChild(opt);
            });
        });

    // Calculate
    calculateBtn.addEventListener('click', async () => {
        errorMsg.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loading.classList.remove('hidden');
        calculateBtn.disabled = true;

        try {
            const model = modelSelect.value;
            let data;

            if (activeTab === 'tc-text') {
                const text = textInput.value.trim();
                if (!text) throw new Error('Please enter some text.');
                const fd = new FormData();
                fd.append('text', text);
                if (model) fd.append('model', model);
                const r = await fetch('/api/token-calculator/calculate/text', { method: 'POST', body: fd });
                if (!r.ok) throw new Error(`Server error: ${r.status}`);
                data = await r.json();
            } else {
                if (!selectedFile) throw new Error('Please select a file.');
                const fd = new FormData();
                fd.append('file', selectedFile);
                if (model) fd.append('model', model);
                const r = await fetch('/api/token-calculator/calculate/file', { method: 'POST', body: fd });
                if (!r.ok) throw new Error(`Server error: ${r.status}`);
                data = await r.json();
            }
            renderResults(data);
        } catch (err) {
            errorMsg.textContent = err.message;
            errorMsg.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
            calculateBtn.disabled = false;
        }
    });

    function fmtCost(c) { return c == null ? '-' : c < 0.000001 ? '$0.000000' : `$${c.toFixed(6)}`; }
    function fmtTokens(t) { return t == null ? 'N/A' : t.toLocaleString(); }
    function fmtCtx(c) { return c >= 1e6 ? `${(c/1e6).toFixed(1)}M` : `${Math.floor(c/1000)}K`; }

    function renderResults(data) {
        let meta = '';
        if (data.filename) meta += `File: <strong>${data.filename}</strong> (${data.file_type || 'text'})`;
        if (data.word_count !== undefined) {
            if (meta) meta += ' &mdash; ';
            meta += `${data.word_count.toLocaleString()} words, ${data.char_count.toLocaleString()} characters`;
        }
        resultsMeta.innerHTML = meta;
        resultsBody.innerHTML = '';
        data.results.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>${r.model}</td><td>${r.provider}</td><td>${fmtCtx(r.context_window)}</td><td>${fmtTokens(r.tokens)}</td><td>${r.method}</td><td>${fmtCost(r.input_cost)}</td><td>${fmtCost(r.cached_input_cost)}</td><td>${fmtCost(r.output_cost)}</td>`;
            resultsBody.appendChild(tr);
        });
        resultsSection.classList.remove('hidden');
    }
});
