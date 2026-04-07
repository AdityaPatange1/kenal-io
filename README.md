# kenal-io

A simple, production-grade agent framework built around four core primitives: **Block**, **Plate**, **Road**, and **Frame**.

## Concepts

| Primitive | Purpose |
|-----------|---------|
| **Block** | The fundamental processing unit. Takes input, applies rules, returns output. |
| **Plate** | The execution plane. Groups blocks under shared context and rules. |
| **Road** | The piping system. Streams data sequentially through blocks and plates. |
| **Frame** | The orchestration engine. Wires everything together and runs the pipeline. |

## Installation

```bash
pip install kenal-io
```

## Quick Start

```python
from kenal import Block, Plate, Road, Frame

# Create blocks with natural-language rules
summarizer = Block(
    name="summarizer",
    rules=["Summarize the input in 2-3 sentences", "Keep technical terms intact"],
)

formatter = Block(
    name="formatter",
    rules=["Format the text with bullet points", "Use markdown"],
)

# Group blocks on a plate with shared rules
analysis = Plate(
    name="analysis",
    blocks=[summarizer],
    rules=["Process all inputs in English"],
)

# Wire blocks together with a road
pipeline = Road(name="main", stops=[analysis, formatter])

# Run everything through a frame
frame = Frame(name="demo", roads=[pipeline])
results = frame.run("Your input text here...")

for result in results:
    print(f"[{result.source_block}] {result.output}")
```

### Using Custom Processors

Blocks can use pure-Python functions instead of the LLM engine:

```python
from kenal import Block, Road, Frame

upper = Block(name="upper", process=lambda data: data.upper())
exclaim = Block(name="exclaim", process=lambda data: f"{data}!")

road = Road(name="transform", stops=[upper, exclaim])
frame = Frame(roads=[road])
results = frame.run("hello world")
# results[-1].output == "HELLO WORLD!"
```

## Configuration

kenal auto-detects the first available model from your local ollama instance. Override via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `KENAL_OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `KENAL_MODEL` | *(auto-detect)* | Force a specific model name |

## CLI

```bash
kenal info            # Show framework info
kenal run config.json "input text"  # Run a pipeline from JSON config
```

## Examples

Numbered scripts in `examples/` walk through blocks, rules, plates, roads, frames, JSON-shaped config (`examples/config/pipeline.json`), and the `kenal` CLI. Run them all in order with colored banners:

```bash
make examples
# or: python -u scripts/run_examples.py
# or: ./scripts/run_examples.sh
```

Run the full pytest suite with the same style of headers and pytest’s own colored output:

```bash
make run-tests
# or: python -u scripts/run_tests.py
# or: ./scripts/run_tests.sh
```

## Development

```bash
make install   # Install in editable mode with dev dependencies
make test      # Run tests (pytest directly)
make run-tests # Tests via scripts/run_tests.py (colored banners + pytest colors)
make examples  # Run all examples sequentially
make lint      # Ruff + mypy
make validate  # lint + test
make build     # Build distributable
make format    # Auto-format code
```

## License

MIT — see [LICENSE](LICENSE).
