document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('xl-drop-zone');
    const fileInput = document.getElementById('xl-file-input');
    const fileInfo = document.getElementById('xl-file-info');
    const sheetTabs = document.getElementById('xl-sheet-tabs');
    const tableArea = document.getElementById('xl-table-area');
    const thead = document.getElementById('xl-thead');
    const tbody = document.getElementById('xl-tbody');
    const csvBtn = document.getElementById('xl-csv-btn');
    const csvAllBtn = document.getElementById('xl-csv-all-btn');
    const loading = document.getElementById('xl-loading');
    const errorDiv = document.getElementById('xl-error');

    let uploadedFile = null;
    let sheetsData = {};
    let activeSheet = '';

    dropZone.addEventListener('click', () => fileInput.click());
    dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
    dropZone.addEventListener('drop', e => {
        e.preventDefault(); dropZone.classList.remove('drag-over');
        if (e.dataTransfer.files.length) loadFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => { if (fileInput.files.length) loadFile(fileInput.files[0]); });

    async function loadFile(file) {
        uploadedFile = file;
        fileInfo.textContent = `${file.name} (${(file.size/1024).toFixed(1)} KB)`;
        fileInfo.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        loading.classList.remove('hidden');
        tableArea.classList.add('hidden');
        sheetTabs.classList.add('hidden');

        const fd = new FormData();
        fd.append('file', file);
        try {
            const r = await fetch('/api/excel-reader/upload', { method: 'POST', body: fd });
            if (!r.ok) throw new Error(`Server error: ${r.status}`);
            const data = await r.json();
            sheetsData = data.sheets;
            const names = Object.keys(sheetsData);

            sheetTabs.innerHTML = '';
            names.forEach((name, i) => {
                const btn = document.createElement('button');
                btn.className = 'tab' + (i === 0 ? ' active' : '');
                btn.textContent = name;
                btn.addEventListener('click', () => showSheet(name));
                sheetTabs.appendChild(btn);
            });
            sheetTabs.classList.remove('hidden');
            showSheet(names[0]);
            tableArea.classList.remove('hidden');
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    }

    function showSheet(name) {
        activeSheet = name;
        sheetTabs.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.textContent === name));
        const rows = sheetsData[name];
        if (!rows || rows.length === 0) { thead.innerHTML = ''; tbody.innerHTML = '<tr><td>Empty sheet</td></tr>'; return; }
        const headers = rows[0];
        thead.innerHTML = '<tr>' + headers.map(h => `<th>${h ?? ''}</th>`).join('') + '</tr>';
        tbody.innerHTML = '';
        rows.slice(1).forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = row.map(c => `<td>${c ?? ''}</td>`).join('');
            tbody.appendChild(tr);
        });
    }

    csvBtn.addEventListener('click', () => downloadCSV(activeSheet));
    csvAllBtn.addEventListener('click', () => downloadCSV('__all__'));

    async function downloadCSV(sheet) {
        if (!uploadedFile) return;
        const fd = new FormData();
        fd.append('file', uploadedFile);
        fd.append('sheet', sheet);
        const r = await fetch('/api/excel-reader/convert-csv', { method: 'POST', body: fd });
        const blob = await r.blob();
        const ext = sheet === '__all__' ? 'zip' : 'csv';
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = uploadedFile.name.replace(/\.xlsx?$/i, '') + (sheet === '__all__' ? '.zip' : `_${sheet}.csv`);
        a.click();
    }
});
