document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('at-drop-zone');
    const fileInput = document.getElementById('at-file-input');
    const fileInfo = document.getElementById('at-file-info');
    const endpointInput = document.getElementById('at-endpoint');
    const typeSelect = document.getElementById('at-type');
    const modelInput = document.getElementById('at-model');
    const transcribeBtn = document.getElementById('at-transcribe-btn');
    const resultArea = document.getElementById('at-result');
    const resultText = document.getElementById('at-result-text');
    const copyBtn = document.getElementById('at-copy-btn');
    const loading = document.getElementById('at-loading');
    const errorDiv = document.getElementById('at-error');

    let currentFile = null;

    // Load saved endpoint from localStorage
    const saved = localStorage.getItem('at-settings');
    if (saved) {
        try {
            const s = JSON.parse(saved);
            if (s.endpoint) endpointInput.value = s.endpoint;
            if (s.type) typeSelect.value = s.type;
            if (s.model) modelInput.value = s.model;
        } catch {}
    }

    function saveSettings() {
        localStorage.setItem('at-settings', JSON.stringify({
            endpoint: endpointInput.value,
            type: typeSelect.value,
            model: modelInput.value,
        }));
    }

    [endpointInput, typeSelect, modelInput].forEach(el => el.addEventListener('change', saveSettings));

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
        currentFile = file;
        fileInfo.textContent = `${file.name} (${(file.size / 1024 / 1024).toFixed(2)} MB)`;
        fileInfo.classList.remove('hidden');
    }

    // Transcribe
    transcribeBtn.addEventListener('click', async () => {
        if (!currentFile) { showError('Please select an audio file'); return; }
        if (!endpointInput.value.trim()) { showError('Please enter an endpoint URL'); return; }

        errorDiv.classList.add('hidden');
        resultArea.classList.add('hidden');
        loading.classList.remove('hidden');
        transcribeBtn.disabled = true;

        const fd = new FormData();
        fd.append('file', currentFile);
        fd.append('endpoint', endpointInput.value.trim());
        fd.append('endpoint_type', typeSelect.value);
        fd.append('model', modelInput.value.trim());

        try {
            const r = await fetch('/api/audio-transcription/transcribe', { method: 'POST', body: fd });
            const data = await r.json();
            if (data.error) throw new Error(data.error);
            resultText.textContent = data.text || '(No transcription returned)';
            resultArea.classList.remove('hidden');
        } catch (err) {
            showError(err.message);
        } finally {
            loading.classList.add('hidden');
            transcribeBtn.disabled = false;
        }
    });

    function showError(msg) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(resultText.textContent);
    });
});
