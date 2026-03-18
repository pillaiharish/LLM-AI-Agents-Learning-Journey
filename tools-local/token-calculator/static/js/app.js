document.addEventListener('DOMContentLoaded', () => {
    const textInput = document.getElementById('text-input');
    const fileInput = document.getElementById('file-input');
    const dropZone = document.getElementById('drop-zone');
    const fileInfo = document.getElementById('file-info');
    const modelSelect = document.getElementById('model-select');
    const calculateBtn = document.getElementById('calculate-btn');
    const resultsSection = document.getElementById('results-section');
    const resultsMeta = document.getElementById('results-meta');
    const resultsBody = document.querySelector('#results-table tbody');
    const loading = document.getElementById('loading');
    const errorMsg = document.getElementById('error-msg');
    const themeToggle = document.getElementById('theme-toggle');
    const statChars = document.getElementById('stat-chars');
    const statWords = document.getElementById('stat-words');
    const statTokens = document.getElementById('stat-tokens');

    let selectedFile = null;
    let activeTab = 'text';

    // Theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);

    themeToggle.addEventListener('click', () => {
        const current = document.documentElement.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    });

    // Tabs
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
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
        const estTokens = Math.max(0, Math.round(words * 1.3));
        statChars.textContent = `${chars.toLocaleString()} characters`;
        statWords.textContent = `${words.toLocaleString()} words`;
        statTokens.textContent = `${estTokens.toLocaleString()} est. tokens`;
    });

    // File drop zone
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', e => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });

    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) {
            setFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length) {
            setFile(fileInput.files[0]);
        }
    });

    function setFile(file) {
        selectedFile = file;
        const sizeKB = (file.size / 1024).toFixed(1);
        fileInfo.textContent = `Selected: ${file.name} (${sizeKB} KB)`;
        fileInfo.classList.remove('hidden');
    }

    // Load models
    fetch('/api/models')
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
            let data;
            const model = modelSelect.value;

            if (activeTab === 'text') {
                const text = textInput.value.trim();
                if (!text) throw new Error('Please enter some text.');

                const formData = new FormData();
                formData.append('text', text);
                if (model) formData.append('model', model);

                const resp = await fetch('/api/calculate/text', { method: 'POST', body: formData });
                if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
                data = await resp.json();
            } else {
                if (!selectedFile) throw new Error('Please select a file.');

                const formData = new FormData();
                formData.append('file', selectedFile);
                if (model) formData.append('model', model);

                const resp = await fetch('/api/calculate/file', { method: 'POST', body: formData });
                if (!resp.ok) throw new Error(`Server error: ${resp.status}`);
                data = await resp.json();
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

    function formatCost(cost) {
        if (cost === null || cost === undefined) return '-';
        if (cost < 0.000001) return '$0.000000';
        return `$${cost.toFixed(6)}`;
    }

    function formatTokens(tokens) {
        if (tokens === null || tokens === undefined) return 'N/A';
        return tokens.toLocaleString();
    }

    function formatContext(ctx) {
        if (ctx >= 1_000_000) return `${(ctx / 1_000_000).toFixed(1)}M`;
        return `${Math.floor(ctx / 1000)}K`;
    }

    function renderResults(data) {
        let meta = '';
        if (data.filename) {
            meta += `File: <strong>${data.filename}</strong> (${data.file_type || 'text'})`;
        }
        if (data.word_count !== undefined) {
            if (meta) meta += ' &mdash; ';
            meta += `${data.word_count.toLocaleString()} words, ${data.char_count.toLocaleString()} characters`;
        }
        resultsMeta.innerHTML = meta;

        resultsBody.innerHTML = '';
        data.results.forEach(r => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${r.model}</td>
                <td>${r.provider}</td>
                <td>${formatContext(r.context_window)}</td>
                <td>${formatTokens(r.tokens)}</td>
                <td>${r.method}</td>
                <td>${formatCost(r.input_cost)}</td>
                <td>${formatCost(r.cached_input_cost)}</td>
                <td>${formatCost(r.output_cost)}</td>
            `;
            resultsBody.appendChild(tr);
        });

        resultsSection.classList.remove('hidden');
    }
});
