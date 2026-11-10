#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError, URLError
import json
import time
import traceback

from app.bioinformatics_engine import analyze_dna_sequence

HOST = "127.0.0.1"
PORT = 8083

MODEL = "qwen-coder"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

TIMEOUT = 600

SYSTEM_PROMPT = """
You are a careful Python and bioinformatics assistant.

ENVIRONMENT
- Python 3.8.10
- Biopython 1.83
- NumPy 1.24.4
- Ubuntu 20.04

BIOLOGICAL RULES
1. DNA transcription converts DNA into RNA. It is NOT translation.
2. RNA transcription replaces T with U in the corresponding sequence.
3. Translation converts nucleotide codons into amino acids.
4. DNA reverse complement means complementing the bases and then reversing the sequence.
5. DNA base pairing: A-T and G-C.
6. RNA base pairing: A-U and G-C.
7. GC percentage = ((G + C) / total valid A,T,G,C bases) * 100.
8. Never calculate GC percentage using only G or using a protein sequence.
9. Distinguish DNA, RNA and protein sequences clearly.
10. Explain reading frames and incomplete codons when relevant.
11. Do not assume every sequence begins with a start codon.
12. Ambiguous nucleotide symbols must not be silently treated as A, T, G or C.

BIOPYTHON API RULES
- Use from Bio.Seq import Seq for sequence operations.
- Use from Bio import SeqIO for FASTA and other supported sequence files.
- Use Seq.transcribe() for DNA-to-RNA transcription.
- Use Seq.translate() for nucleotide-to-protein translation.
- Use Seq.reverse_complement() for DNA reverse complement.
- Use len(sequence) for sequence length.
- Use sequence.count("A"), sequence.count("T"),
  sequence.count("G") and sequence.count("C") for base counts.
- Do not invent imports, classes, functions or methods.
- Do not confuse reverse complement, transcription and translation.

PYTHON CODE RULES
- Write code compatible with Python 3.8.10.
- Provide complete runnable programs when requested.
- Include necessary imports.
- Use meaningful variable names.
- Handle empty sequences and invalid input when relevant.
- Do not claim code was executed unless it was actually executed.
- Explain important calculations and expected output.
- If uncertain about an API, say so instead of inventing one.

SCIENTIFIC ACCURACY
- Check biological definitions before answering.
- Show calculation steps for numerical answers.
- Verify that reported counts add up to the sequence length.
- State assumptions about sequence orientation, reading frame and genetic code.
- Clearly distinguish established facts from assumptions.
- Never invent experimental results or biological interpretations.
- Recommend independent validation for scientific conclusions.

RESPONSE STYLE
- Use clear, simple scientific language.
- Explain concepts step by step.
- Use examples where helpful.
- Correctly label DNA, RNA and protein outputs.
- Admit uncertainty rather than provide a confident but unsupported answer.

Your priority is biological correctness, valid Python code and honest explanations.
"""

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bioinformatics AI V3 Fixed</title>

<style>
body {
    margin: 0;
    background: #111827;
    color: white;
    font-family: Arial, sans-serif;
}
header {
    background: #1f2937;
    padding: 20px;
    text-align: center;
}
#chat {
    max-width: 900px;
    margin: 20px auto;
    height: 65vh;
    overflow-y: auto;
    padding: 12px;
}
.message {
    padding: 14px;
    margin: 12px 0;
    border-radius: 10px;
    white-space: pre-wrap;
    line-height: 1.6;
    overflow-wrap: anywhere;
}
.user {
    background: #1d4ed8;
    margin-left: 12%;
}
.ai {
    background: #263449;
    margin-right: 8%;
}
#input-area {
    max-width: 900px;
    margin: auto;
    display: flex;
    gap: 10px;
    padding: 12px;
}
textarea {
    flex: 1;
    padding: 14px;
    background: #1f2937;
    color: white;
    border: 1px solid #4b5563;
    border-radius: 8px;
}
button {
    padding: 12px 20px;
    background: #16a34a;
    color: white;
    border: 0;
    border-radius: 7px;
}
button:disabled {
    opacity: 0.5;
}
select {
    padding: 12px;
    background: #1f2937;
    color: white;
    border: 1px solid #4b5563;
    border-radius: 8px;
}
#status {
    text-align: center;
    padding: 10px;
    color: #9ca3af;
}
</style>
</head>

<body>

<header>
<h2>Bioinformatics AI Assistant</h2>
<p>Offline Python, Biopython and Computational Biology</p>
</header>

<div id="chat">
<div class="message ai">
Welcome! Ask your bioinformatics question.
</div>
</div>

<div id="status">Connected to local interface</div>

<div id="input-area">
<select id="mode" onchange="updateMode()">
<option value="chat">AI Chat</option>
<option value="dna">DNA Analysis</option>
</select>
<textarea id="question" rows="3"
placeholder="Ask your question..."></textarea>
<button id="send" onclick="sendMessage()">Send</button>
</div>

<script>

let messages = [];
let busy = false;

function addMessage(text, type) {
    let div = document.createElement("div");
    div.className = "message " + type;
    div.textContent = text;
    document.getElementById("chat").appendChild(div);
    div.scrollIntoView({behavior: "smooth"});
}

function updateMode() {
    let mode = document.getElementById("mode").value;
    let input = document.getElementById("question");
    let status = document.getElementById("status");

    if (mode === "dna") {
        input.placeholder = "Paste your DNA sequence here...";
        status.textContent = "DNA Analysis | Biopython engine";
    } else {
        input.placeholder = "Ask your bioinformatics question...";
        status.textContent = "Connected to local interface";
    }
}

async function sendMessage() {

    if (busy) return;

    let input = document.getElementById("question");
    let button = document.getElementById("send");
    let status = document.getElementById("status");

    let question = input.value.trim();
    let isDNA = document.getElementById("mode").value === "dna";

    if (!question) return;

    busy = true;
    button.disabled = true;

    addMessage(question, "user");

    if (!isDNA) {
        messages.push({
            role: "user",
            content: question
        });
    }

    input.value = "";
    status.textContent = isDNA
        ? "Analyzing with Biopython..."
        : "Qwen is thinking...";

    let timer;

    try {

        const controller = new AbortController();

        timer = setTimeout(() => controller.abort(), 600000);

        if (isDNA) {
            const response = await fetch("/api/analyze-dna", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({sequence: question}),
                signal: controller.signal
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "DNA analysis failed");
            }

            const r = data.result;

            let gcText = r.GC_percentage === null
                ? "Not defined (no canonical bases)"
                : r.GC_percentage.toFixed(2) + "%";

            let answer =
                "DNA SEQUENCE ANALYSIS REPORT\n" +
                "================================\n\n" +
                "1. SEQUENCE INFORMATION\n" +
                "Sequence length : " + r.sequence_length + " bp\n" +
                "GC content      : " + gcText + "\n\n" +
                "2. NUCLEOTIDE COUNTS\n" +
                "A : " + r.A + "\n" +
                "T : " + r.T + "\n" +
                "G : " + r.G + "\n" +
                "C : " + r.C + "\n" +
                "Total canonical bases : " +
                    (r.A + r.T + r.G + r.C) + "\n\n" +
                "3. SEQUENCE TRANSFORMATIONS\n" +
                "Reverse complement:\n" + r.reverse_complement + "\n\n" +
                "RNA transcript:\n" + r.RNA + "\n\n" +
                "4. PROTEIN TRANSLATION\n" +
                "Reading frame : 0 (first nucleotide)\n" +
                "Protein       : " + r.protein_frame_0 + "\n" +
                "Incomplete trailing bases : " +
                    r.incomplete_trailing_bases + "\n\n" +
                "Note: Translation uses complete codons in frame 0. " +
                "Incomplete trailing bases are excluded.";

            addMessage(answer, "ai");
            status.textContent = "DNA Analysis completed | Biopython";
            return;
        }

        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({messages: messages}),
            signal: controller.signal
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Server error");
        }

        let answer = data.message.content;

        messages.push({
            role: "assistant",
            content: answer
        });

        addMessage(answer, "ai");

        status.textContent = "Connected | Qwen Coder";

    } catch (error) {

        if (!isDNA) {
            messages.pop();
        }

        let message = error.name === "AbortError"
            ? "Request timed out after 10 minutes."
            : error.message;

        addMessage("Error: " + message, "ai");

        status.textContent = "Request failed";

    } finally {

        clearTimeout(timer);
        busy = false;
        button.disabled = false;

    }
}

document.getElementById("question").addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    }
);

</script>
</body>
</html>
"""


# IMPORTANT:
# This opener explicitly bypasses the campus HTTP proxy.
LOCAL_OPENER = build_opener(ProxyHandler({}))


class ChatHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path != "/":
            self.send_error(404)
            return

        content = HTML.encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        self.wfile.write(content)

    def do_POST(self):

        if self.path == "/api/analyze-dna":
            try:
                length = int(self.headers.get("Content-Length", "0"))

                if length <= 0 or length > 1000000:
                    self.send_json({"error": "Invalid request size."}, 413)
                    return

                data = json.loads(
                    self.rfile.read(length).decode("utf-8")
                )

                result = analyze_dna_sequence(data.get("sequence", ""))

                self.send_json({"result": result})
                return

            except (ValueError, TypeError) as error:
                self.send_json({"error": str(error)}, 400)
                return

            except Exception as error:
                print("[DNA ANALYSIS] Error:", repr(error), flush=True)
                traceback.print_exc()
                self.send_json({"error": "DNA analysis failed."}, 500)
                return

        if self.path != "/api/chat":
            self.send_error(404)
            return

        start = time.time()

        try:

            length = int(self.headers.get("Content-Length", "0"))

            if length <= 0 or length > 1000000:
                self.send_json({"error": "Invalid request size."}, 413)
                return

            data = json.loads(
                self.rfile.read(length).decode("utf-8")
            )

            history = data.get("messages", [])

            if not isinstance(history, list):
                self.send_json({"error": "Invalid messages."}, 400)
                return

            history = history[-12:]

            payload = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ] + history,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_ctx": 2048
                }
            }

            request = Request(
                OLLAMA_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )

            with LOCAL_OPENER.open(
                request,
                timeout=TIMEOUT
            ) as response:

                result = json.loads(
                    response.read().decode("utf-8")
                )

            print(
                "[V3 FIXED] Completed in {:.2f}s".format(
                    time.time() - start
                ),
                flush=True
            )

            self.send_json(result)

        except HTTPError as error:

            details = error.read().decode(
                "utf-8", errors="replace"
            )

            print("[V3 FIXED] HTTP error:", details, flush=True)

            self.send_json(
                {"error": "Ollama HTTP error: " + str(error.code)},
                502
            )

        except URLError as error:

            print("[V3 FIXED] Connection error:", repr(error), flush=True)

            self.send_json(
                {"error": "Local Ollama connection failed."},
                502
            )

        except Exception as error:

            print("[V3 FIXED] Error:", repr(error), flush=True)

            traceback.print_exc()

            self.send_json(
                {"error": str(error)},
                500
            )

    def send_json(self, data, status=200):

        content = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        self.wfile.write(content)

    def log_message(self, format, *args):
        print("[V3 FIXED]", format % args, flush=True)


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        (HOST, PORT),
        ChatHandler
    )

    print("=" * 45)
    print("BIOINFORMATICS AI ASSISTANT V3 FIXED")
    print("=" * 45)
    print("Address: http://127.0.0.1:8083")
    print("Model:", MODEL)
    print("Proxy bypass: Enabled")
    print("Timeout:", TIMEOUT)
    print("=" * 45)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server.")
    finally:
        server.server_close()
