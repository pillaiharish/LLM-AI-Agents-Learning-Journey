document.addEventListener('DOMContentLoaded', () => {
    const scanBtn = document.getElementById('ns-scan-btn');
    const devicesDiv = document.getElementById('ns-devices');
    const devicesBody = document.getElementById('ns-devices-body');
    const scanLoading = document.getElementById('ns-scan-loading');
    const pingBtn = document.getElementById('ns-ping-btn');
    const pingHost = document.getElementById('ns-ping-host');
    const pingResult = document.getElementById('ns-ping-result');
    const pingLoading = document.getElementById('ns-ping-loading');
    const speedBtn = document.getElementById('ns-speed-btn');
    const speedResult = document.getElementById('ns-speed-result');
    const speedLoading = document.getElementById('ns-speed-loading');
    const errorDiv = document.getElementById('ns-error');

    scanBtn.addEventListener('click', async () => {
        errorDiv.classList.add('hidden');
        devicesDiv.classList.add('hidden');
        scanLoading.classList.remove('hidden');
        try {
            const r = await fetch('/api/network-scanner/scan', { method: 'POST' });
            const data = await r.json();
            devicesBody.innerHTML = '';
            data.devices.forEach(d => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${d.ip}</td><td>${d.mac}</td><td>${d.hostname || '-'}</td>`;
                devicesBody.appendChild(tr);
            });
            devicesDiv.classList.remove('hidden');
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            scanLoading.classList.add('hidden');
        }
    });

    pingBtn.addEventListener('click', async () => {
        errorDiv.classList.add('hidden');
        pingResult.classList.add('hidden');
        pingLoading.classList.remove('hidden');
        try {
            const r = await fetch(`/api/network-scanner/ping?host=${encodeURIComponent(pingHost.value)}`);
            const data = await r.json();
            pingResult.textContent = data.output;
            pingResult.classList.remove('hidden');
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            pingLoading.classList.add('hidden');
        }
    });

    speedBtn.addEventListener('click', async () => {
        errorDiv.classList.add('hidden');
        speedResult.classList.add('hidden');
        speedLoading.classList.remove('hidden');
        try {
            const r = await fetch('/api/network-scanner/speedtest', { method: 'POST' });
            const data = await r.json();
            if (data.error) throw new Error(data.error);
            speedResult.innerHTML = `
                <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem;margin-top:0.5rem;">
                    <div class="card" style="text-align:center;">
                        <div class="text-muted" style="font-size:0.8rem;">Download</div>
                        <div style="font-size:1.5rem;font-weight:700;color:var(--green);">${data.download}</div>
                        <div class="text-muted" style="font-size:0.75rem;">Mbps</div>
                    </div>
                    <div class="card" style="text-align:center;">
                        <div class="text-muted" style="font-size:0.8rem;">Upload</div>
                        <div style="font-size:1.5rem;font-weight:700;color:var(--blue);">${data.upload}</div>
                        <div class="text-muted" style="font-size:0.75rem;">Mbps</div>
                    </div>
                    <div class="card" style="text-align:center;">
                        <div class="text-muted" style="font-size:0.8rem;">Ping</div>
                        <div style="font-size:1.5rem;font-weight:700;color:var(--accent);">${data.ping}</div>
                        <div class="text-muted" style="font-size:0.75rem;">ms</div>
                    </div>
                </div>
                <div class="text-muted mt-1" style="font-size:0.8rem;">Server: ${data.server || 'N/A'}</div>`;
            speedResult.classList.remove('hidden');
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        } finally {
            speedLoading.classList.add('hidden');
        }
    });
});
