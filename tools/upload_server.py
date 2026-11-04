#!/usr/bin/env python3
"""LAN upload server: receives files and saves them to <project>/uploads/.

Upload only: no listing, no download, no delete. Open to anyone on the
network; set UPLOAD_TOKEN to require ?t=<token> on every request.

    python3 tools/upload_server.py            # port 8765
    python3 tools/upload_server.py --port 9000
"""
import argparse
import html
import os
import re
import secrets
import socket
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
UPLOADS = ROOT / "uploads"
CHUNK = 1024 * 1024
MAX_BYTES = 20 * 1024**3  # 20 GB per file

PAGE = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Upload motion-cena</title>
<style>
  :root{color-scheme:light dark;--bg:#111;--fg:#eee;--mute:#999;--acc:#e8c547;--line:#333}
  body{margin:0;font:16px system-ui,sans-serif;background:var(--bg);color:var(--fg)}
  main{max-width:560px;margin:0 auto;padding:32px 16px}
  h1{font-size:22px;margin:0 0 4px} p{color:var(--mute);margin:0 0 24px}
  label{display:block;border:2px dashed var(--line);border-radius:12px;padding:40px 16px;
        text-align:center;cursor:pointer} label.over{border-color:var(--acc)}
  input{display:none}
  ul{list-style:none;padding:0;margin:24px 0 0}
  li{padding:10px 0;border-bottom:1px solid var(--line);font-size:14px}
  .bar{height:4px;background:var(--line);border-radius:2px;margin-top:6px;overflow:hidden}
  .bar i{display:block;height:100%;width:0;background:var(--acc)}
  .ok{color:#6c6} .err{color:#e66}
</style></head><body><main>
<h1>Enviar para motion-cena/uploads</h1>
<p>Toque para escolher ou arraste arquivos aqui.</p>
<label id="drop">Escolher arquivos<input id="f" type="file" multiple></label>
<ul id="list"></ul>
</main><script>
const token = "__TOKEN__";
const list = document.getElementById("list"), drop = document.getElementById("drop");
function send(file){
  const li = document.createElement("li");
  li.innerHTML = '<span></span><div class="bar"><i></i></div>';
  li.firstChild.textContent = file.name;
  list.prepend(li);
  const xhr = new XMLHttpRequest();
  xhr.open("PUT", "/upload?t=" + token);
  xhr.setRequestHeader("X-Filename", encodeURIComponent(file.name));
  xhr.upload.onprogress = e => { if (e.lengthComputable) li.querySelector("i").style.width = (e.loaded / e.total * 100) + "%"; };
  xhr.onload = () => {
    const s = li.firstChild;
    if (xhr.status === 201) { s.className = "ok"; s.textContent = "ok  " + xhr.responseText; }
    else { s.className = "err"; s.textContent = "erro  " + file.name + " (" + xhr.responseText + ")"; }
  };
  xhr.onerror = () => { li.firstChild.className = "err"; li.firstChild.textContent = "falhou  " + file.name; };
  xhr.send(file);
}
document.getElementById("f").onchange = e => { [...e.target.files].forEach(send); e.target.value = ""; };
drop.ondragover = e => { e.preventDefault(); drop.classList.add("over"); };
drop.ondragleave = () => drop.classList.remove("over");
drop.ondrop = e => { e.preventDefault(); drop.classList.remove("over"); [...e.dataTransfer.files].forEach(send); };
</script></body></html>"""


def safe_name(raw: str) -> str:
    try:  # http.server decodes headers as latin-1; recover raw UTF-8
        raw = raw.encode("latin-1").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    name = os.path.basename(unquote(raw).replace("\\", "/"))
    name = unicodedata.normalize("NFC", name)
    name = re.sub(r"[^\w.\- ()]+", "_", name).strip(" .")
    return name[:180] or "arquivo"


def unique_path(name: str) -> Path:
    path = UPLOADS / name
    stem, suffix = path.stem, path.suffix
    n = 1
    while path.exists():
        path = UPLOADS / f"{stem} ({n}){suffix}"
        n += 1
    return path


class Handler(BaseHTTPRequestHandler):
    token = ""

    def authorized(self) -> bool:
        if not self.token:
            return True
        given = parse_qs(urlparse(self.path).query).get("t", [""])[0]
        return secrets.compare_digest(given, self.token)

    def reply(self, code: int, body: str, ctype="text/plain; charset=utf-8"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if urlparse(self.path).path != "/" or not self.authorized():
            return self.reply(404, "not found")
        self.reply(200, PAGE.replace("__TOKEN__", html.escape(self.token)), "text/html; charset=utf-8")

    def do_PUT(self):
        if urlparse(self.path).path != "/upload" or not self.authorized():
            return self.reply(403, "forbidden")
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            return self.reply(411, "length required")
        if length > MAX_BYTES:
            return self.reply(413, "too large")

        UPLOADS.mkdir(exist_ok=True)
        dest = unique_path(safe_name(self.headers.get("X-Filename", "arquivo")))
        tmp = dest.with_name(dest.name + ".part")
        remaining = length
        try:
            with open(tmp, "wb") as out:
                while remaining:
                    chunk = self.rfile.read(min(CHUNK, remaining))
                    if not chunk:
                        raise ConnectionError("client disconnected")
                    out.write(chunk)
                    remaining -= len(chunk)
            tmp.rename(dest)
        except Exception:
            tmp.unlink(missing_ok=True)
            raise
        self.log_message("saved %s (%d bytes)", dest.name, length)
        self.reply(201, dest.name)


def lan_ip() -> str:
    for probe in ("8.8.8.8", "10.255.255.255"):  # UDP connect sends nothing
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            try:
                s.connect((probe, 80))
                ip = s.getsockname()[0]
            except OSError:
                continue
            if not ip.startswith("127."):
                return ip
    return "127.0.0.1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()

    Handler.token = os.environ.get("UPLOAD_TOKEN", "")
    UPLOADS.mkdir(exist_ok=True)
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Salvando em: {UPLOADS}")
    query = f"?t={Handler.token}" if Handler.token else ""
    print(f"Abra no celular/PC da rede: http://{lan_ip()}:{args.port}/{query}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
