document.addEventListener('DOMContentLoaded', () => {
    const textArea    = document.getElementById('mc-text');
    const dropZone    = document.getElementById('mc-drop-zone');
    const fileInput   = document.getElementById('mc-file-input');
    const fileInfo    = document.getElementById('mc-file-info');
    const previewBtn  = document.getElementById('mc-preview-btn');
    const step2       = document.getElementById('mc-step2');
    const previewFrame = document.getElementById('mc-preview-frame');
    const dlHtmlBtn      = document.getElementById('mc-dl-html-btn');
    const previewPdfBtn  = document.getElementById('mc-preview-pdf-btn');
    const dlPdfBtn       = document.getElementById('mc-dl-pdf-btn');
    const togglePreviewBtn = document.getElementById('mc-toggle-preview-btn');
    const loading        = document.getElementById('mc-loading');
    const pdfLoading     = document.getElementById('mc-pdf-loading');
    const pdfFrame       = document.getElementById('mc-pdf-frame');
    const errorDiv       = document.getElementById('mc-error');

    let uploadedFile = null;    // File object if user uploaded
    let activeTab = 'mc-paste';
    let currentHtmlBlob = null; // Blob for the generated HTML
    let currentPdfBlob = null;  // Blob for the generated PDF
    let currentPdfUrl  = null;  // Object URL for PDF iframe
    let currentFileStem = 'document'; // filename without extension

    // ── Tabs ────────────────────────────────────────────────────────────────
    document.querySelectorAll('#page-md-converter .tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('#page-md-converter .tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('#page-md-converter .tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            activeTab = tab.dataset.tab;
            document.getElementById(`tab-${activeTab}`).classList.add('active');
        });
    });

    // ── File upload ──────────────────────────────────────────────────────────
    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) setFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) setFile(fileInput.files[0]); });

    function setFile(file) {
        uploadedFile = file;
        currentFileStem = file.name.replace(/\.(md|markdown|txt)$/i, '');
        fileInfo.textContent = `${file.name}  (${(file.size / 1024).toFixed(1)} KB)`;
        fileInfo.classList.remove('hidden');

        // Also populate the textarea so user can see the content
        const reader = new FileReader();
        reader.onload = e => { textArea.value = e.target.result; };
        reader.readAsText(file);
    }

    // ── Step 1 → Step 2: Preview + HTML download ────────────────────────────
    previewBtn.addEventListener('click', async () => {
        const mdText = textArea.value.trim();
        if (!mdText) { showError('Please enter or upload some Markdown first.'); return; }
        hideError();
        step2.classList.add('hidden');
        // Reset PDF preview state
        if (currentPdfUrl) { URL.revokeObjectURL(currentPdfUrl); currentPdfUrl = null; }
        currentPdfBlob = null;
        pdfFrame.src = '';
        pdfFrame.classList.add('hidden');
        dlPdfBtn.classList.add('hidden');
        loading.classList.remove('hidden');
        previewBtn.disabled = true;
        currentFileStem = uploadedFile
            ? uploadedFile.name.replace(/\.(md|markdown|txt)$/i, '')
            : 'document';

        try {
            // Get rendered HTML for in-browser preview
            const fd = buildFormData('preview');
            const r = await fetch('/api/md-converter/preview', { method: 'POST', body: fd });
            if (!r.ok) throw new Error(`Server error ${r.status}`);
            const data = await r.json();
            if (data.error) throw new Error(data.error);

            // Render inside the iframe via srcdoc
            previewFrame.srcdoc = data.html;

            // Pre-fetch the HTML as a Blob for the download button
            const fd2 = buildFormData('html');
            const r2 = await fetch('/api/md-converter/to-html', { method: 'POST', body: fd2 });
            if (!r2.ok) throw new Error(`HTML conversion error ${r2.status}`);
            currentHtmlBlob = await r2.blob();

            step2.classList.remove('hidden');
            step2.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (err) {
            showError(err.message);
        } finally {
            loading.classList.add('hidden');
            previewBtn.disabled = false;
        }
    });

    // ── Toggle iframe ────────────────────────────────────────────────────────
    togglePreviewBtn.addEventListener('click', () => {
        const visible = previewFrame.style.display !== 'none';
        previewFrame.style.display = visible ? 'none' : '';
        togglePreviewBtn.textContent = visible ? 'Show Preview' : 'Toggle Preview';
    });

    // ── Download HTML ────────────────────────────────────────────────────────
    dlHtmlBtn.addEventListener('click', () => {
        if (!currentHtmlBlob) return;
        triggerDownload(currentHtmlBlob, `${currentFileStem}.html`);
    });

    // ── Step 3: Preview PDF ──────────────────────────────────────────────────
    previewPdfBtn.addEventListener('click', async () => {
        const mdText = textArea.value.trim();
        if (!mdText) return;
        hideError();
        pdfLoading.classList.remove('hidden');
        pdfFrame.classList.add('hidden');
        dlPdfBtn.classList.add('hidden');
        previewPdfBtn.disabled = true;

        // Revoke previous object URL to free memory
        if (currentPdfUrl) { URL.revokeObjectURL(currentPdfUrl); currentPdfUrl = null; }

        try {
            const fd = buildFormData('pdf');
            const r = await fetch('/api/md-converter/to-pdf', { method: 'POST', body: fd });
            if (!r.ok) { const t = await r.text(); throw new Error(t); }
            currentPdfBlob = await r.blob();
            currentPdfUrl  = URL.createObjectURL(currentPdfBlob);

            pdfFrame.src = currentPdfUrl;
            pdfFrame.classList.remove('hidden');
            dlPdfBtn.classList.remove('hidden');
            pdfFrame.scrollIntoView({ behavior: 'smooth', block: 'start' });
        } catch (err) {
            showError(err.message);
        } finally {
            pdfLoading.classList.add('hidden');
            previewPdfBtn.disabled = false;
        }
    });

    // ── Step 3: Download PDF (after preview) ────────────────────────────────
    dlPdfBtn.addEventListener('click', () => {
        if (!currentPdfBlob) return;
        triggerDownload(currentPdfBlob, `${currentFileStem}.pdf`);
    });

    // ── Helpers ──────────────────────────────────────────────────────────────
    function buildFormData(mode) {
        const fd = new FormData();
        if (uploadedFile && activeTab === 'mc-upload') {
            fd.append('file', uploadedFile);
        } else {
            fd.append('text', textArea.value);
            fd.append('filename', currentFileStem + '.md');
        }
        return fd;
    }

    function triggerDownload(blob, filename) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        setTimeout(() => URL.revokeObjectURL(url), 5000);
    }

    function showError(msg) {
        errorDiv.textContent = msg;
        errorDiv.classList.remove('hidden');
    }

    function hideError() {
        errorDiv.classList.add('hidden');
    }
});
