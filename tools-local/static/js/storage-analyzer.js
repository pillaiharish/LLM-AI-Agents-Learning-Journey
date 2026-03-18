document.addEventListener('DOMContentLoaded', () => {
    const pathInput = document.getElementById('sa-path');
    const scanBtn = document.getElementById('sa-scan-btn');
    const results = document.getElementById('sa-results');
    const usageBar = document.getElementById('sa-usage-bar');
    const usageText = document.getElementById('sa-usage-text');
    const topBody = document.getElementById('sa-top-body');
    const loading = document.getElementById('sa-loading');
    const errorDiv = document.getElementById('sa-error');

    function fmtSize(bytes) {
        if (bytes >= 1e12) return (bytes / 1e12).toFixed(2) + ' TB';
        if (bytes >= 1e9) return (bytes / 1e9).toFixed(2) + ' GB';
        if (bytes >= 1e6) return (bytes / 1e6).toFixed(2) + ' MB';
        if (bytes >= 1e3) return (bytes / 1e3).toFixed(1) + ' KB';
        return bytes + ' B';
    }

    scanBtn.addEventListener('click', async () => {
        errorDiv.classList.add('hidden');
        results.classList.add('hidden');
        loading.classList.remove('hidden');

        try {
            const r = await fetch('/api/storage-analyzer/scan', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: pathInput.value }),
            });
            if (!r.ok) { const t = await r.text(); throw new Error(t); }
            const data = await r.json();

            const pct = ((data.used / data.total) * 100).toFixed(1);
            usageBar.style.width = pct + '%';
            usageBar.textContent = pct + '%';
            usageText.textContent = `${fmtSize(data.used)} used of ${fmtSize(data.total)} (${fmtSize(data.available)} available)`;

            topBody.innerHTML = '';
            const maxSize = data.top_paths.length ? data.top_paths[0].size : 1;
            data.top_paths.forEach(p => {
                const pctBar = ((p.size / maxSize) * 100).toFixed(0);
                const tr = document.createElement('tr');
                tr.innerHTML = `<td style="max-width:400px;overflow:hidden;text-overflow:ellipsis;" title="${p.path}">${p.path}</td><td style="white-space:nowrap;">${fmtSize(p.size)}</td><td style="width:120px;"><div class="progress-bar"><div class="progress-fill" style="width:${pctBar}%;"></div></div></td>`;
                topBody.appendChild(tr);
            });

            results.classList.remove('hidden');
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            loading.classList.add('hidden');
        }
    });
});
