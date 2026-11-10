#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError, URLError
import json
import time
import traceback

HOST = "127.0.0.1"
PORT = 8083

MODEL = "qwen-coder"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

TIMEOUT = 600

SYSTEM_PROMPT = """
You are an offline bioinformatics and Python assistant.

Environment:
Python 3.8.10
Biopython 1.83
NumPy 1.24.4
Ubuntu 20.04

Use correct Biopython imports and APIs.
Use from Bio import SeqIO.
Use Bio.Seq for sequence operations.
Use transcribe() for RNA transcription.
Use translate() for protein translation.
Use reverse_complement() for reverse complement.
Never invent APIs.
Write complete Python programs when requested.
Explain biological assumptions.
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

async function sendMessage() {

    if (busy) return;

    let input = document.getElementById("question");
    let button = document.getElementById("send");
    let status = document.getElementById("status");

    let question = input.value.trim();

    if (!question) return;

    busy = true;
    button.disabled = true;

    addMessage(question, "user");

    messages.push({
        role: "user",
        content: question
    });

    input.value = "";
    status.textContent = "Qwen is thinking...";

    let timer;

    try {

        const controller = new AbortController();

        timer = setTimeout(() => controller.abort(), 600000);

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

        messages.pop();

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
