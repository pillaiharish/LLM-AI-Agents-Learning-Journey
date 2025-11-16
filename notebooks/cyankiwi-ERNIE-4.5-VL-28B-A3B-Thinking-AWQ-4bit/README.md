# ERNIE-4.5-VL-28B-A3B-Thinking-AWQ-4bit — Colab vLLM Notebook

This folder contains the notebook `ernie_4_5_vl_colab.ipynb`. The goal was to run the model `cyankiwi/ERNIE-4.5-VL-28B-A3B-Thinking-AWQ-4bit` on an A100 (≈40GB VRAM) using two approaches:

- Transformers (direct load)
- vLLM (OpenAI-compatible API)

Ultimately, we pivoted to a vLLM-only notebook because the Transformers path repeatedly failed on the quantized artifact. The last state of this notebook focuses on vLLM.

## Environment

- Colab GPU runtime (Linux)
- Python 3.12
- GPU: NVIDIA A100 (≈40GB)

## Attempts and Errors (Chronological)

### 1) Transformers path (direct load)

The model repo contains quantization metadata that routes the load through the `compressed_tensors` integration in Transformers, even though the title includes "AWQ".

Errors encountered:

- Missing dependency when loading:

```
ImportError: compressed_tensors is not installed and is required for compressed-tensors quantization. Please install it with `pip install compressed-tensors`.
```

- After installing, generation failed due to a mismatch between the model's remote code (MoE/VLM) and compressed linear layer implementation:

```
AttributeError: 'CompressedLinear' object has no attribute 'weight'
  at modeling_ernie4_5_vl.py line ~726:
  current_device = self.gate_proj.weight.data.device
```

What we tried:
- Patched compressed linear layers to expose a `.weight` attribute via `__getattr__`
- Created fallback dummy tensors for `.weight` so `.weight.data.device` resolves
- Reordered patch to run BEFORE model load
- Searched import paths for compressed linear classes inside `compressed_tensors`

Result:
- Patches reduced import issues but generation still crashed when the remote modeling code accessed `.weight`. The artifact’s compressed-tensors integration appears incompatible with the model’s custom MoE/VLM forward path in Transformers.

Conclusion:
- The model card recommends using vLLM for this exact reason. We moved to the vLLM path.

### 2) vLLM path (recommended by the model card)

Initial steps:
- Install vLLM nightly wheels
- Start the OpenAI-compatible server
- Send chat completions (text and image+text)

Errors and fixes:

- Pip flag not supported (fixed):
```
no such option: --index-strategy
```
We removed the unsupported flag.

- CLI not found (fixed by using module entrypoint):
```
FileNotFoundError: [Errno 2] No such file or directory: 'vllm'
```
We switched to launching with:
```
python -m vllm.entrypoints.openai.api_server
```

- Server not becoming ready (still unresolved):
```
⚠ vLLM server not ready yet; check logs
ConnectionRefusedError / MaxRetryError to http://127.0.0.1:8000
```
We added:
- Early process-death detection
- Health check before client request
- Log viewer to tail `/tmp/vllm_server.log`

Despite these, the server failed to bind/readiness. Likely causes:
- Torch/CUDA wheel mismatch in the current Colab runtime
- CUDA drivers missing required symbols for the selected vLLM wheel
- Remote modeling code requirements that need specific vLLM version/flags

## Current State (Left as-is)

- Notebook is now vLLM-only (Transformers path removed to avoid confusion)
- Installation cell installs `vllm` and verifies import
- Server start cell launches the API server via module entrypoint and waits for readiness
- Client cells for text-only and image+text requests
- Log tailing cell for `/tmp/vllm_server.log`
- Shutdown cell to terminate the vLLM server

The last run failed to reach server readiness. We left it at "check logs and adjust". See the log viewer cell in the notebook for details.

## What to Try Next

1) Inspect logs
- Run the log tail cell to print the last 100 lines of `/tmp/vllm_server.log` and share the error lines.

2) Pin versions compatible with your Colab runtime
- Try installing vLLM with a CUDA index matching your runtime (e.g., cu121 or cu129) and a compatible Torch build. Example:

```bash
pip install -U --pre vllm \
  --extra-index-url https://wheels.vllm.ai/nightly
```

If the runtime provides a different CUDA, we may need to align Torch/CUDA or switch to a different vLLM wheel index.

3) Try the base model with vLLM
- The quantized artifact might have packaging specifics. Testing `baidu/ERNIE-4.5-VL-28B-A3B-Thinking` in vLLM could clarify if the issue lies in the quantized repo.

4) Try a known-good VLM with vLLM or Transformers
- For a sanity check on the environment, try `OpenGVLab/InternVL2-8B-AWQ` or `Qwen/Qwen2-VL-7B-Instruct` to verify the pipeline.

## How to Use the Notebook

1) Verify GPU (top cell)
2) Install vLLM (prints versions)
3) Start server (prints command, waits for readiness)
4) Run text-only client cell
5) Optional: run image+text client cell
6) If it fails, run the log viewer cell and adjust versions/flags as needed
7) Stop server to free resources

## Known Caveats

- Colab images can vary; a fresh runtime may pull different Torch/CUDA wheels than expected
- Some vLLM features/flags mentioned in third-party docs aren’t official vLLM options; we removed non-standard flags
- The ERNIE quantized artifact appears to force a compressed-tensors path in Transformers; vLLM avoids this but still needs compatible wheels

## Files in this folder

- `ernie_4_5_vl_colab.ipynb` — vLLM-only notebook with install, server start, client examples, logs, and shutdown
- `README.md` — this file

## License

Follows the repository’s root `LICENSE` (Apache-2.0 as indicated by the model card).