document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('img-drop-zone');
    const fileInput = document.getElementById('img-file-input');
    const editor = document.getElementById('img-editor');
    const preview = document.getElementById('img-preview');
    const info = document.getElementById('img-info');
    const loading = document.getElementById('img-loading');
    const errorDiv = document.getElementById('img-error');

    const widthInput = document.getElementById('img-width');
    const heightInput = document.getElementById('img-height');
    const lockAspect = document.getElementById('img-lock-aspect');
    const resizeBtn = document.getElementById('img-resize-btn');
    const formatSelect = document.getElementById('img-format');
    const convertBtn = document.getElementById('img-convert-btn');
    const brightness = document.getElementById('img-brightness');
    const saturation = document.getElementById('img-saturation');
    const hue = document.getElementById('img-hue');
    const adjustBtn = document.getElementById('img-adjust-btn');

    let currentFile = null;
    let origWidth = 0, origHeight = 0, aspectRatio = 1;

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault(); dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) loadImage(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) loadImage(fileInput.files[0]); });

    function loadImage(file) {
        currentFile = file;
        const url = URL.createObjectURL(file);
        preview.onload = () => {
            origWidth = preview.naturalWidth;
            origHeight = preview.naturalHeight;
            aspectRatio = origWidth / origHeight;
            widthInput.value = origWidth;
            heightInput.value = origHeight;
            info.textContent = `${file.name} - ${origWidth}x${origHeight} - ${(file.size/1024).toFixed(1)} KB`;
        };
        preview.src = url;
        editor.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        // Reset adjustments
        brightness.value = 100; saturation.value = 100; hue.value = 0;
        document.getElementById('img-brightness-val').textContent = '100';
        document.getElementById('img-saturation-val').textContent = '100';
        document.getElementById('img-hue-val').textContent = '0';
        preview.style.filter = '';
    }

    // Aspect ratio lock
    widthInput.addEventListener('input', () => {
        if (lockAspect.checked && widthInput.value) {
            heightInput.value = Math.round(widthInput.value / aspectRatio);
        }
    });
    heightInput.addEventListener('input', () => {
        if (lockAspect.checked && heightInput.value) {
            widthInput.value = Math.round(heightInput.value * aspectRatio);
        }
    });

    // CSS filter preview
    [brightness, saturation, hue].forEach(slider => {
        slider.addEventListener('input', () => {
            document.getElementById('img-brightness-val').textContent = brightness.value;
            document.getElementById('img-saturation-val').textContent = saturation.value;
            document.getElementById('img-hue-val').textContent = hue.value;
            preview.style.filter = `brightness(${brightness.value}%) saturate(${saturation.value}%) hue-rotate(${hue.value}deg)`;
        });
    });

    async function postImage(endpoint, extraFields = {}) {
        if (!currentFile) return;
        errorDiv.classList.add('hidden');
        loading.classList.remove('hidden');
        const fd = new FormData();
        fd.append('file', currentFile);
        Object.entries(extraFields).forEach(([k,v]) => fd.append(k, v));
        try {
            const r = await fetch(endpoint, { method: 'POST', body: fd });
            if (!r.ok) { const t = await r.text(); throw new Error(t); }
            const blob = await r.blob();
            const cd = r.headers.get('Content-Disposition') || '';
            const match = cd.match(/filename="?([^"]+)"?/);
            const filename = match ? match[1] : 'output';
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            a.click();
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    }

    resizeBtn.addEventListener('click', () => {
        postImage('/api/image-tools/resize', { width: widthInput.value, height: heightInput.value });
    });

    convertBtn.addEventListener('click', () => {
        postImage('/api/image-tools/convert', { format: formatSelect.value });
    });

    adjustBtn.addEventListener('click', () => {
        postImage('/api/image-tools/adjust', {
            brightness: brightness.value,
            saturation: saturation.value,
            hue: hue.value,
        });
    });
});
