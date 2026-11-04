#!/usr/bin/env node
// motion-cena studio: chat with a coding agent on the left, the live HyperFrames
// Studio of the project being edited on the right, pipeline stages on top.
//
//   node tools/studio/server.mjs [--port 4400] [--no-open]
//
// No dependencies (Node 22+). Binds to 127.0.0.1 only. The agent runs headless
// with auto-approval (it cannot ask permission through a web page), so use it
// only on your own machine.

import http from "node:http";
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..", "..");
const PROJECTS = path.join(ROOT, "projects");
const CREATIVES = path.join(ROOT, "creatives");

const argv = process.argv.slice(2);
const flag = (name) => argv.includes(`--${name}`);
const opt = (name, dflt) => {
  const i = argv.indexOf(`--${name}`);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : dflt;
};
const PORT = Number(opt("port", process.env.MOTION_CENA_STUDIO_PORT || 4400));
const TOKEN = crypto.randomBytes(16).toString("hex");

// ── Agents ──────────────────────────────────────────────────────────────────
// Each adapter builds the headless command and turns its JSON stream into
// normalized events: text | tool | tool_result | session | done | error.

const short = (s, n = 400) => {
  s = String(s ?? "").trim();
  return s.length > n ? s.slice(0, n) + " …" : s;
};
const describeInput = (input = {}) =>
  input.command || input.file_path || input.path || input.pattern || input.url || input.description || input.prompt || JSON.stringify(input);

const AGENTS = {
  claude: {
    label: "Claude Code",
    bin: "claude",
    args: (prompt, session) => [
      "-p", prompt,
      "--output-format", "stream-json", "--verbose",
      "--dangerously-skip-permissions",
      ...(session ? ["--resume", session] : []),
    ],
    parse(ev, emit) {
      if (ev.type === "system" && ev.subtype === "init") emit({ type: "session", id: ev.session_id });
      else if (ev.type === "assistant") {
        for (const c of ev.message?.content ?? []) {
          if (c.type === "text" && c.text?.trim()) emit({ type: "text", text: c.text });
          else if (c.type === "tool_use") emit({ type: "tool", name: c.name, detail: short(describeInput(c.input), 300) });
        }
      } else if (ev.type === "user") {
        for (const c of ev.message?.content ?? []) {
          if (c.type !== "tool_result") continue;
          const text = Array.isArray(c.content) ? c.content.map((x) => x.text ?? "").join("\n") : c.content;
          emit({ type: "tool_result", text: short(text), error: !!c.is_error });
        }
      } else if (ev.type === "result") {
        emit({ type: "session", id: ev.session_id });
        if (ev.is_error) emit({ type: "error", text: short(ev.result || ev.subtype || "erro do Claude Code", 1200) });
        emit({ type: "done", ok: !ev.is_error });
      }
    },
  },
  codex: {
    label: "Codex",
    bin: "codex",
    args: (prompt, session) => {
      const common = ["--json", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox"];
      return session ? ["exec", "resume", ...common, session, prompt] : ["exec", ...common, prompt];
    },
    parse(ev, emit) {
      const it = ev.item ?? {};
      if (ev.type === "thread.started") emit({ type: "session", id: ev.thread_id });
      else if (ev.type === "item.started" && it.type === "command_execution") emit({ type: "tool", name: "shell", detail: short(it.command, 300) });
      else if (ev.type === "item.completed") {
        if (it.type === "agent_message") emit({ type: "text", text: it.text });
        else if (it.type === "command_execution") emit({ type: "tool_result", text: short(it.aggregated_output), error: it.exit_code !== 0 });
        else if (it.type === "file_change") emit({ type: "tool", name: "edit", detail: (it.changes ?? []).map((c) => `${c.kind ?? ""} ${c.path}`.trim()).join(", ") });
        else if (it.type && it.type !== "reasoning") emit({ type: "tool", name: it.type, detail: short(it.text ?? it.query ?? "", 300) });
      } else if (ev.type === "turn.completed") emit({ type: "done", ok: true });
      else if (ev.type === "turn.failed" || ev.type === "error") emit({ type: "error", text: short(ev.error?.message ?? ev.message ?? JSON.stringify(ev)) });
    },
  },
  agy: {
    label: "Antigravity",
    bin: "agy",
    args: (prompt, session) => [
      "-p", prompt,
      "--output-format", "stream-json",
      "--dangerously-skip-permissions",
      ...(session ? ["--conversation", session] : []),
    ],
    parse(ev, emit) {
      if (ev.event === "init") emit({ type: "session", id: ev.conversation_id });
      else if (ev.event === "step_update") {
        const s = ev.step_update ?? {};
        if (s.step_type === "agent_response" && s.text_delta) emit({ type: "text", text: s.text_delta, delta: true });
        else if (s.step_type === "tool" && s.state === "ACTIVE") {
          const p = s.tool_info?.parameters ?? {};
          emit({ type: "tool", name: s.tool_name, detail: short(p.CommandLine ?? p.Path ?? p.AbsolutePath ?? p.TargetFile ?? JSON.stringify(p), 300) });
        } else if (s.step_type === "tool" && s.state === "DONE") emit({ type: "tool_result", text: short(s.tool_info?.output ?? "") });
      } else if (ev.event === "result") {
        const r = ev.result ?? {};
        emit({ type: "session", id: r.conversation_id });
        if (r.status !== "SUCCESS") emit({ type: "error", text: short(r.error || `Antigravity terminou com status ${r.status}`, 1200) });
        emit({ type: "done", ok: r.status === "SUCCESS" });
      }
    },
  },
};

const installed = (bin) => spawnSync("sh", ["-c", `command -v ${bin}`], { encoding: "utf8" }).status === 0;
const AVAILABLE = Object.entries(AGENTS)
  .filter(([, a]) => installed(a.bin))
  .map(([id, a]) => ({ id, label: a.label }));

// ── Live events (SSE) ───────────────────────────────────────────────────────

const clients = new Set();
const history = []; // chat events, replayed when the page reloads
const broadcast = (ev) => {
  const line = `data: ${JSON.stringify(ev)}\n\n`;
  for (const res of clients) res.write(line);
};
const chatEvent = (ev) => {
  history.push(ev);
  if (history.length > 2000) history.splice(0, history.length - 2000);
  broadcast({ channel: "chat", ...ev });
};

// ── Agent runs ──────────────────────────────────────────────────────────────

const sessions = {}; // agent id -> session/thread/conversation id
let run = null; // { child, agent }

function startRun(agentId, prompt) {
  const agent = AGENTS[agentId];
  if (!agent || !AVAILABLE.some((a) => a.id === agentId)) throw new Error(`agente indisponível: ${agentId}`);
  if (run) throw new Error("o agente ainda está trabalhando");
  chatEvent({ type: "user", text: prompt, agent: agentId });
  const child = spawn(agent.bin, agent.args(prompt, sessions[agentId]), {
    cwd: ROOT,
    env: { ...process.env, MOTION_CENA_UI: "1" },
    stdio: ["ignore", "pipe", "pipe"],
    detached: true,
  });
  run = { child, agent: agentId };
  broadcast({ channel: "run", running: true, agent: agentId });
  let finished = false;
  let explained = false;
  let err = "";
  const emit = (ev) => {
    if (ev.type === "session") {
      if (ev.id) sessions[agentId] = ev.id;
      return;
    }
    if (ev.type === "error") explained = true;
    if (ev.type === "done") {
      if (!ev.ok && !explained && err.trim()) chatEvent({ type: "error", text: short(err, 1200), agent: agentId });
      finished = true;
    }
    chatEvent({ ...ev, agent: agentId });
  };
  let buf = "";
  child.stdout.on("data", (chunk) => {
    buf += chunk;
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      try {
        agent.parse(JSON.parse(line), emit);
      } catch {
        emit({ type: "log", text: short(line) });
      }
    }
  });
  child.stderr.on("data", (chunk) => (err = (err + chunk).slice(-4000)));
  child.on("close", (code, signal) => {
    if (!finished) {
      if (signal) emit({ type: "error", text: "interrompido" });
      else if (code !== 0) emit({ type: "error", text: short(err || `saiu com código ${code}`, 1200) });
      emit({ type: "done", ok: code === 0 });
    }
    run = null;
    broadcast({ channel: "run", running: false, agent: agentId });
    refreshAll();
  });
  child.on("error", (e) => emit({ type: "error", text: e.message }));
}

function stopRun() {
  if (!run) return;
  try {
    process.kill(-run.child.pid, "SIGTERM");
  } catch {
    run.child.kill("SIGTERM");
  }
}

// ── Projects and pipeline stages ────────────────────────────────────────────

const exists = (...p) => fs.existsSync(path.join(...p));
const isDir = (p) => {
  try {
    return fs.statSync(p).isDirectory();
  } catch {
    return false;
  }
};
const SKIP = new Set(["node_modules", ".hyperframes", "out", ".git", "renders", "snapshots"]);

function latestMtime(dir, depth = 3) {
  let t = 0;
  let entries = [];
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return 0;
  }
  for (const e of entries) {
    if (SKIP.has(e.name)) continue;
    const p = path.join(dir, e.name);
    try {
      t = Math.max(t, fs.statSync(p).mtimeMs);
    } catch {}
    if (e.isDirectory() && depth > 0) t = Math.max(t, latestMtime(p, depth - 1));
  }
  return t;
}

function outputs(slug) {
  const out = [];
  for (const kind of ["reels", "carrossel", "post"]) {
    const dir = path.join(CREATIVES, kind);
    let names = [];
    try {
      names = fs.readdirSync(dir);
    } catch {}
    for (const n of names) if (n.startsWith(`${slug}-`)) out.push(`${kind}/${n}`);
  }
  return out.sort();
}

function compositions(slug) {
  const d = path.join(PROJECTS, slug);
  const found = [];
  let names = [];
  try {
    names = fs.readdirSync(d);
  } catch {}
  for (const n of names.filter((n) => n === "video" || n.startsWith("video-")).sort()) {
    if (exists(d, n, "index.html")) found.push(n);
  }
  if (exists(d, "carousel", "render", "index.html")) found.push("carousel/render");
  return found;
}

function projectState(slug) {
  const d = path.join(PROJECTS, slug);
  const has = (p) => exists(d, p);
  const outs = outputs(slug);
  const carousel = has("carousel") && !has("video");
  const stages = carousel
    ? [
        { id: "brief", label: "Brief", done: has("brief.md"), file: "brief.md" },
        { id: "plano", label: "Plano", done: has("plan.md"), file: "plan.md" },
        { id: "slides", label: "Slides", done: has("carousel/claude-design/project") || has("carousel/render/index.html") },
        { id: "legenda", label: "Legenda", done: has("carousel/legenda.txt"), file: "carousel/legenda.txt" },
        { id: "export", label: "Export", done: outs.some((o) => o.startsWith("carrossel/")) },
      ]
    : [
        { id: "brief", label: "Brief", done: has("brief.md"), file: "brief.md" },
        { id: "roteiro", label: "Roteiro", done: has("plan.md") || has("narration.txt"), file: has("plan.md") ? "plan.md" : "narration.txt" },
        { id: "storyboard", label: "Storyboard", done: has("storyboard.json"), file: "storyboard.json" },
        { id: "marca", label: "Marca", done: has("brand.json"), file: "brand.json" },
        { id: "voz", label: "Locução", done: has("audio/words.json") || has("audio/voice.mp3"), file: "audio/voice.mp3" },
        { id: "timeline", label: "Timeline", done: has("timeline.json"), file: "timeline.json" },
        { id: "animacao", label: "Animação", done: compositions(slug).length > 0 },
        { id: "som", label: "Som", done: has("audio/mix.wav") },
        { id: "render", label: "Render", done: outs.some((o) => o.endsWith(".mp4")) },
      ];
  return { slug, kind: carousel ? "carrossel" : "video", mtime: latestMtime(d), stages, compositions: compositions(slug), outputs: outs };
}

function listProjects() {
  let names = [];
  try {
    names = fs.readdirSync(PROJECTS).filter((n) => !n.startsWith(".") && !n.startsWith("_") && isDir(path.join(PROJECTS, n)));
  } catch {}
  return names.map(projectState).sort((a, b) => b.mtime - a.mtime);
}

// ── HyperFrames Studio previews ─────────────────────────────────────────────

const previews = {}; // "<slug>/<comp>" -> { state, studioUrl }
const starting = new Set();

function hyperframes(args, cwd) {
  return new Promise((resolve) => {
    const child = spawn("npx", ["-y", "hyperframes", ...args], { cwd, stdio: ["ignore", "pipe", "pipe"] });
    let out = "";
    child.stdout.on("data", (c) => (out += c));
    child.on("close", () => {
      const start = out.indexOf("{");
      try {
        resolve(JSON.parse(out.slice(start)));
      } catch {
        resolve(null);
      }
    });
    child.on("error", () => resolve(null));
  });
}

function setPreview(key, value) {
  const prev = previews[key];
  previews[key] = value;
  if (prev?.studioUrl !== value.studioUrl || prev?.state !== value.state) broadcast({ channel: "preview", key, ...value });
}

async function previewStatus(slug, comp) {
  const dir = path.join(PROJECTS, slug, comp);
  const r = await hyperframes(["preview", "--status", "--json"], dir);
  const res = r?.result ?? {};
  const value = { state: res.state ?? "unknown", studioUrl: res.studioUrl ?? null };
  setPreview(`${slug}/${comp}`, value);
  return value;
}

async function ensurePreview(slug, comp) {
  const key = `${slug}/${comp}`;
  const dir = path.join(PROJECTS, slug, comp);
  if (!exists(dir, "index.html")) return { state: "missing" };
  if (previews[key]?.state === "running") return previews[key];
  if (starting.has(key)) return { state: "starting" };
  starting.add(key);
  setPreview(key, { state: "starting", studioUrl: null });
  try {
    const st = await previewStatus(slug, comp);
    if (st.state === "running") return st;
    await hyperframes(["preview", "--background", "--no-open"], dir);
    return await previewStatus(slug, comp);
  } finally {
    starting.delete(key);
  }
}

// ── File watching ───────────────────────────────────────────────────────────

let pending = new Set();
let timer = null;
function onChange(base, file) {
  if (!file) return;
  const parts = file.split(path.sep);
  if (parts.some((p) => SKIP.has(p))) return;
  if (base === PROJECTS) pending.add(parts[0]);
  clearTimeout(timer);
  timer = setTimeout(() => {
    const slugs = [...pending];
    pending = new Set();
    broadcast({ channel: "fs", slugs, projects: listProjects() });
  }, 400);
}
function refreshAll() {
  broadcast({ channel: "fs", slugs: [], projects: listProjects() });
}
for (const dir of [PROJECTS, CREATIVES]) {
  fs.mkdirSync(dir, { recursive: true });
  try {
    fs.watch(dir, { recursive: true }, (_e, f) => onChange(dir, f));
  } catch (e) {
    console.warn(`sem watch em ${dir}: ${e.message}`);
  }
}

// ── HTTP ────────────────────────────────────────────────────────────────────

const MIME = {
  ".html": "text/html; charset=utf-8", ".json": "application/json; charset=utf-8", ".md": "text/plain; charset=utf-8",
  ".txt": "text/plain; charset=utf-8", ".mp4": "video/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav",
  ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".pdf": "application/pdf",
};

function send(res, code, body, type = "application/json; charset=utf-8") {
  res.writeHead(code, { "content-type": type, "cache-control": "no-store", "x-content-type-options": "nosniff" });
  res.end(typeof body === "string" || Buffer.isBuffer(body) ? body : JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let b = "";
    req.on("data", (c) => {
      b += c;
      if (b.length > 1e6) reject(new Error("corpo grande demais"));
    });
    req.on("end", () => {
      try {
        resolve(b ? JSON.parse(b) : {});
      } catch (e) {
        reject(e);
      }
    });
  });
}

function safeFile(base, rel) {
  const p = path.resolve(base, rel ?? "");
  return p.startsWith(base + path.sep) ? p : null;
}

function serveFile(req, res, file) {
  let st;
  try {
    st = fs.statSync(file);
  } catch {
    return send(res, 404, { error: "não existe" });
  }
  if (!st.isFile()) return send(res, 404, { error: "não é arquivo" });
  const type = MIME[path.extname(file).toLowerCase()] ?? "application/octet-stream";
  const range = /bytes=(\d*)-(\d*)/.exec(req.headers.range ?? "");
  if (range) {
    const start = range[1] ? Number(range[1]) : 0;
    const end = range[2] ? Number(range[2]) : st.size - 1;
    res.writeHead(206, { "content-type": type, "content-range": `bytes ${start}-${end}/${st.size}`, "accept-ranges": "bytes", "content-length": end - start + 1 });
    return fs.createReadStream(file, { start, end }).pipe(res);
  }
  res.writeHead(200, { "content-type": type, "content-length": st.size, "accept-ranges": "bytes", "cache-control": "no-store" });
  fs.createReadStream(file).pipe(res);
}

const HOSTS = new Set([`127.0.0.1:${PORT}`, `localhost:${PORT}`]);

const server = http.createServer(async (req, res) => {
  // Block DNS rebinding and cross-site requests: only our own host, only with the session token.
  if (!HOSTS.has(req.headers.host)) return send(res, 403, { error: "host não permitido" });
  const url = new URL(req.url, `http://${req.headers.host}`);
  const p = url.pathname;

  if (req.method === "GET" && p === "/") {
    const html = fs.readFileSync(path.join(HERE, "index.html"), "utf8").replace("__MOTION_CENA_TOKEN__", TOKEN);
    return send(res, 200, html, MIME[".html"]);
  }

  const token = req.headers["x-motion-cena-token"] ?? url.searchParams.get("t");
  if (token !== TOKEN) return send(res, 401, { error: "token inválido" });

  try {
    if (req.method === "GET" && p === "/api/events") {
      res.writeHead(200, { "content-type": "text/event-stream", "cache-control": "no-store", connection: "keep-alive" });
      res.write(`data: ${JSON.stringify({ channel: "hello", running: !!run, agent: run?.agent ?? null })}\n\n`);
      clients.add(res);
      const ka = setInterval(() => res.write(": ping\n\n"), 20000);
      req.on("close", () => {
        clearInterval(ka);
        clients.delete(res);
      });
      return;
    }
    if (req.method === "GET" && p === "/api/state") {
      return send(res, 200, { agents: AVAILABLE, running: !!run, agent: run?.agent ?? null, projects: listProjects(), previews, history, root: ROOT });
    }
    if (req.method === "GET" && p === "/api/file") {
      const base = url.searchParams.get("base") === "creatives" ? CREATIVES : PROJECTS;
      const file = safeFile(base, url.searchParams.get("path"));
      if (!file) return send(res, 400, { error: "caminho inválido" });
      return serveFile(req, res, file);
    }
    if (req.method !== "POST") return send(res, 404, { error: "rota não existe" });
    const body = await readBody(req);
    if (p === "/api/chat") {
      if (!String(body.prompt ?? "").trim()) return send(res, 400, { error: "mensagem vazia" });
      startRun(body.agent, String(body.prompt));
      return send(res, 200, { ok: true });
    }
    if (p === "/api/stop") {
      stopRun();
      return send(res, 200, { ok: true });
    }
    if (p === "/api/reset") {
      if (run) return send(res, 409, { error: "pare o agente antes" });
      for (const k of Object.keys(sessions)) delete sessions[k];
      history.length = 0;
      broadcast({ channel: "reset" });
      return send(res, 200, { ok: true });
    }
    if (p === "/api/preview") {
      const slug = String(body.slug ?? "");
      const comp = String(body.comp ?? "video");
      if (!safeFile(PROJECTS, path.join(slug, comp))) return send(res, 400, { error: "caminho inválido" });
      return send(res, 200, await ensurePreview(slug, comp));
    }
    return send(res, 404, { error: "rota não existe" });
  } catch (e) {
    return send(res, 400, { error: e.message });
  }
});

server.listen(PORT, "127.0.0.1", () => {
  const link = `http://127.0.0.1:${PORT}/`;
  console.log(`motion-cena studio em ${link}`);
  console.log(`agentes encontrados: ${AVAILABLE.map((a) => a.label).join(", ") || "nenhum (instale Claude Code, Codex ou Antigravity)"}`);
  console.log("o agente roda com aprovação automática; use só na sua máquina. Ctrl+C para sair.");
  if (!flag("no-open")) {
    const opener = process.platform === "darwin" ? "open" : process.platform === "win32" ? "start" : "xdg-open";
    spawn(opener, [link], { stdio: "ignore", detached: true, shell: process.platform === "win32" }).on("error", () => {}).unref();
  }
});

process.on("SIGINT", () => {
  stopRun();
  process.exit(0);
});
