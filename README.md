# Bioinformatics AI Assistant

An offline, locally hosted AI coding assistant for bioinformatics programming using Ollama, Qwen2.5-Coder, Python, and Biopython.

The project combines a browser-based chat interface with a local language model and bioinformatics sequence-analysis scripts.

## Features

### Local AI Assistant
- Browser-based chat interface.
- Local LLM inference using Ollama.
- Qwen2.5-Coder model integration.
- Conversation context during a chat session.
- Local communication without cloud AI APIs.
- Configured for Python and bioinformatics assistance.

### DNA Sequence Analysis
- FASTA file reading using Biopython.
- Sequence length calculation.
- A, T, G, and C nucleotide counts.
- GC percentage calculation.
- Reverse complement generation.
- DNA-to-RNA transcription.
- Protein translation in reading frame 0.

## Technology Stack

| Component | Technology |
|---|---|
| Operating System | Ubuntu 20.04 |
| Programming Language | Python 3.8 |
| AI Runtime | Ollama |
| Language Model | Qwen2.5-Coder 0.5B |
| Bioinformatics Library | Biopython 1.83 |
| Numerical Library | NumPy 1.24.4 |
| Interface | HTML, CSS, JavaScript |

## Project Structure

```text
Bioinformatics-AI-Assistant/
├── app/
│   └── local_ai_chat_v3_fixed.py
├── projects/
│   └── sequence_analysis/
│       ├── data/
│       ├── scripts/
│       │   └── dna_analyzer_v6.py
│       └── results/
├── requirements.txt
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

### 1. Install Ollama

https://ollama.com/download



### 2. Prepare the Qwen2.5-Coder model

This project uses Qwen2.5-Coder 0.5B Instruct in GGUF format through Ollama.

The model file is not included in this repository. Users must obtain a compatible GGUF model file separately.

Create a file named `Modelfile` with the following configuration:

`FROM /absolute/path/to/your-model.gguf`

Replace the example path with the actual location of your GGUF file.

Create the Ollama model using:

`ollama create qwen-coder -f Modelfile`

Verify the model using:

`ollama list`

The application uses the model name `qwen-coder`, configured in `app/local_ai_chat_v3_fixed.py`.

**Note:** The original development workstation already has this model installed locally. No additional model download or creation is required on that machine.






### 3. Clone the repository

```bash
git clone https://github.com/AryaAlgo/Bioinformatics-AI-Assistant.git
cd Bioinformatics-AI-Assistant
```

### 4. Create a Python virtual environment

```bash
python3 -m venv bioenv
source bioenv/bin/activate
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Start Ollama

```bash
ollama serve
```

If Ollama is already running as a system service, this step is unnecessary.

### 7. Start the AI assistant

```bash
python app/local_ai_chat_v3_fixed.py
```

Open http://127.0.0.1:8083 in your browser on the same machine.

## Running the DNA Analyzer

```bash
python projects/sequence_analysis/scripts/dna_analyzer_v6.py projects/sequence_analysis/data/sample.fasta
```

## Architecture

```text
User
  |
  v
Browser Chat Interface
  |
  v
Python HTTP Server
  |
  v
Local Ollama API
  |
  v
Qwen2.5-Coder Model
  |
  v
AI Response
```

## Important Notes and Limitations

- The assistant binds to `127.0.0.1` and is intended for local use.
- Model files are not included in this repository.
- AI-generated code and biological interpretations should be independently verified.
- The DNA analyzer translates sequences in reading frame 0; it does not perform ORF prediction.
- Incomplete trailing codon bases are excluded before translation.
- Ambiguous nucleotide symbols are excluded from the GC percentage denominator.
- CSV export and biological reading-frame validation are not currently implemented.

## Privacy

Chat requests are processed through the locally configured Ollama instance. No external cloud AI API is configured in this project.

## Future Improvements

- Open reading frame identification.
- CSV export.
- Improved nucleotide validation.
- Additional sequence-analysis workflows.
- Improved model accuracy and bioinformatics evaluation.

## Author

**AryaAlgo**

GitHub: https://github.com/AryaAlgo

---

This project is intended for learning, experimentation, and local bioinformatics programming assistance.
