# JSON vs TOON vs VSC — Token Benchmark Notebook

This folder contains the notebook `json_toon_vsc_token_benchmark.ipynb`, which compares prompt token usage across three text formats derived from the same data:

- JSON (original structured text)
- TOON (a compact table-like text with a header and CSV rows)
- VSC (an even more compact, value-only CSV text)

The notebook converts a sample JSON payload into TOON and VSC, then counts tokens for each using OpenAI’s `tiktoken` library. It also prints a simple cost estimate example so you can reason about prompting costs at scale.

## What the notebook does

1. Installs `tiktoken` (one-time in Colab)
2. Defines two converters:
   - `json_to_toon(json_str)`: Produces a header like `products[3]{id,name,price}:` followed by CSV rows
   - `json_to_vsc(json_str)`: Outputs only the essential values in CSV rows (e.g., `Laptop,3999.90`)
3. Builds the three text payloads: JSON, TOON, and VSC
4. Counts tokens for each payload
   - Tries `tiktoken.encoding_for_model("gpt-4o")`
   - Falls back to `cl100k_base` if that model name isn’t available in your local tokenizer
5. Prints a comparison table and a rough cost estimate for a batch of calls

## Why this is useful

Compact text formats can reduce token usage and therefore cost and latency. 
This notebook lets you quickly see how much you might save by moving from verbose JSON to a compact schema like TOON or VSC for your prompts.

## Requirements

- Python environment capable of running Jupyter/Colab
- `tiktoken` (installed by the first cell if you’re in Colab)

If you’re running locally, you can install `tiktoken` via:

```bash
pip install tiktoken
```

## How to run

- Open `json_toon_vsc_token_benchmark.ipynb` in Colab or VS Code/Jupyter
- Run all cells from top to bottom
- Review the printed outputs:
  - The three payloads (JSON/TOON/VSC)
  - Token counts and % vs JSON
  - Rough cost estimate for a configurable number of calls

## Customizing the benchmark

- Replace the sample JSON
  - Edit `sample_json` to reflect your real data structure
- Change fields in TOON output
  - Update the `fields` list in `json_to_toon()` and adjust the CSV row accordingly
- Simplify VSC further
  - Modify `json_to_vsc()` to include only the minimal data needed by your prompts
- Choose a different tokenizer/encoding
  - Change the model name in `encoding_for_model("gpt-4o")`
  - Or set a different base like `cl100k_base` / `o200k_base` if you target other models
- Adjust cost math
  - Edit `price_per_million` and the number of calls in `cost_for()` to match your pricing

## Notes

- Token counts vary by tokenizer and model family. Always use the encoding that matches your target model when possible.
- `tiktoken.encoding_for_model()` raises `KeyError` if the model isn’t recognized; the notebook falls back to a known base encoding.
- JSON may be easier for you to read and debug, but compact formats often perform better in cost-sensitive pipelines.

## File list

- `json_toon_vsc_token_benchmark.ipynb`: The notebook
- `README.md`: This guide

## License

This notebook follows the license of the parent repository. See the root-level `LICENSE` file for details.
