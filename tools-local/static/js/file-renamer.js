document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('rn-drop-zone');
    const fileInput = document.getElementById('rn-file-input');
    const editor = document.getElementById('rn-editor');
    const currentName = document.getElementById('rn-current');
    const newNameInput = document.getElementById('rn-new-name');
    const renameBtn = document.getElementById('rn-rename-btn');
    const randomBtn = document.getElementById('rn-random-btn');
    const stripBtn = document.getElementById('rn-strip-btn');
    const errorDiv = document.getElementById('rn-error');

    let currentFile = null;

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
        currentName.value = file.name;
        const ext = file.name.includes('.') ? '.' + file.name.split('.').pop() : '';
        newNameInput.value = file.name.replace(ext, '') + ext;
        editor.classList.remove('hidden');
        errorDiv.classList.add('hidden');
    }

    async function doRename(action) {
        if (!currentFile) return;
        errorDiv.classList.add('hidden');
        const fd = new FormData();
        fd.append('file', currentFile);
        fd.append('action', action);
        if (action === 'custom') fd.append('new_name', newNameInput.value);

        try {
            const r = await fetch('/api/file-renamer/rename', { method: 'POST', body: fd });
            if (!r.ok) { const t = await r.text(); throw new Error(t); }
            const blob = await r.blob();
            const cd = r.headers.get('Content-Disposition') || '';
            const match = cd.match(/filename="?([^"]+)"?/);
            const filename = match ? match[1] : 'renamed_file';
            const a = document.createElement('a');
            a.href = URL.createObjectURL(blob);
            a.download = filename;
            a.click();
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    }

    renameBtn.addEventListener('click', () => doRename('custom'));
    randomBtn.addEventListener('click', () => doRename('random'));
    stripBtn.addEventListener('click', () => doRename('strip'));
});
