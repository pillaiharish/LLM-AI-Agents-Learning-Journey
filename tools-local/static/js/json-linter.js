document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('jl-input');
    const lineNums = document.getElementById('jl-line-numbers');
    const lintBtn = document.getElementById('jl-lint-btn');
    const copyBtn = document.getElementById('jl-copy-btn');
    const minifyBtn = document.getElementById('jl-minify-btn');
    const clearBtn = document.getElementById('jl-clear-btn');
    const pasteBtn = document.getElementById('jl-paste-btn');
    const fileInput = document.getElementById('jl-file-input');
    const status = document.getElementById('jl-status');
    const errorsDiv = document.getElementById('jl-errors');

    function updateLineNumbers() {
        const lines = input.value.split('\n').length;
        lineNums.innerHTML = Array.from({ length: lines }, (_, i) => i + 1).join('<br>');
    }

    input.addEventListener('input', updateLineNumbers);
    input.addEventListener('scroll', () => { lineNums.scrollTop = input.scrollTop; });
    updateLineNumbers();

    clearBtn.addEventListener('click', () => {
        input.value = '';
        updateLineNumbers();
        status.classList.add('hidden');
        errorsDiv.classList.add('hidden');
    });

    pasteBtn.addEventListener('click', async () => {
        try {
            const text = await navigator.clipboard.readText();
            input.value = text;
            updateLineNumbers();
        } catch { /* clipboard denied */ }
    });

    fileInput.addEventListener('change', () => {
        if (!fileInput.files.length) return;
        const reader = new FileReader();
        reader.onload = e => { input.value = e.target.result; updateLineNumbers(); };
        reader.readAsText(fileInput.files[0]);
    });

    lintBtn.addEventListener('click', async () => {
        status.classList.add('hidden');
        errorsDiv.classList.add('hidden');
        const text = input.value.trim();
        if (!text) return;

        try {
            const r = await fetch('/api/json-linter/lint', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text }),
            });
            const data = await r.json();

            if (data.valid) {
                input.value = data.formatted;
                updateLineNumbers();
                status.className = 'msg-success';
                status.textContent = 'Valid JSON - formatted successfully';
                status.classList.remove('hidden');
            } else {
                status.className = 'msg-error';
                status.textContent = `Invalid JSON - ${data.errors.length} error(s) found`;
                status.classList.remove('hidden');

                let html = '<div style="margin-top:0.5rem;">';
                data.errors.forEach(e => {
                    html += `<div style="padding:0.4rem 0;font-size:0.85rem;border-bottom:1px solid var(--border);">`;
                    html += `<span class="text-red">Line ${e.line}, Col ${e.col}:</span> ${e.message}`;
                    html += `</div>`;
                });
                html += '</div>';
                errorsDiv.innerHTML = html;
                errorsDiv.classList.remove('hidden');
            }
        } catch (err) {
            status.className = 'msg-error';
            status.textContent = 'Error: ' + err.message;
            status.classList.remove('hidden');
        }
    });

    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(input.value);
    });

    minifyBtn.addEventListener('click', () => {
        try {
            const obj = JSON.parse(input.value);
            input.value = JSON.stringify(obj);
            updateLineNumbers();
        } catch { /* not valid */ }
    });
});
