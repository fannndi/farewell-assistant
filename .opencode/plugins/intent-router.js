// Run precision pipeline on every user message.
// Blocking: waits for pipeline to complete (PIPELINE_TIMEOUT env or 60s default).
// Prepend footer to user message parts — project awareness + pipeline status.
// Security: User input passed as separate argv arg, NOT interpolated into shell command.

const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const PIPELINE_TIMEOUT = parseInt(process.env.PIPELINE_TIMEOUT || "60000", 10);
const LOG_DIR = ".opencode" + path.sep + "logs";

function logError(msg) {
    try {
        const logPath = path.join(".opencode", "logs", "plugin-error.log");
        const ts = new Date().toISOString();
        fs.appendFileSync(logPath, `[${ts}] ${msg}\n`);
    } catch (_) {}
}

exports.server = async (ctx) => {
    return {
        "chat.message": async (_input, output) => {
            try {
                const text = extractText(output?.parts);
                if (!text || text.length < 3) return;

                const py = findPython(ctx.directory);
                const callTime = Date.now();

                let pipelineFailed = false;
                try {
                    execFileSync(
                        py,
                        ["-m", "farewell_assistant.run_router", "--input", text],
                        {
                            cwd: ctx.directory,
                            timeout: PIPELINE_TIMEOUT,
                            windowsHide: true,
                            stdio: "ignore",
                        }
                    );
                } catch (e) {
                    pipelineFailed = true;
                    logError(`Pipeline exec error: ${e.message || e}`);
                }

                const pipelinePath = path.join(ctx.directory, ".opencode", "pipeline-result.json");
                if (!fs.existsSync(pipelinePath)) {
                    if (pipelineFailed) {
                        output.parts.unshift({ type: "text", text: `[PIPELINE ERROR] Gagal menjalankan pipeline. Cek .opencode/logs/plugin-error.log\n` });
                    }
                    return;
                }

                let raw, data;
                try {
                    raw = fs.readFileSync(pipelinePath, "utf-8").replace(/^\uFEFF/, "");
                    data = JSON.parse(raw);
                } catch (e) {
                    logError(`Pipeline parse error: ${e.message || e}`);
                    output.parts.unshift({ type: "text", text: `[PIPELINE ERROR] Gagal parse pipeline result.\n` });
                    return;
                }
                if (!data || !data.intent) return;

                // Staleness check — pipeline result older than call = stale
                const pipelineTime = new Date(data.timestamp).getTime() || 0;
                if (pipelineTime < callTime - 2000) {
                    output.parts.unshift({ type: "text", text: `[TIMEOUT] Pipeline timeout. Mode: ${(data.profile || "eco").charAt(0).toUpperCase() + (data.profile || "eco").slice(1)}\n` });
                    return;
                }

                // HOLD — input too vague
                if (data.blocked === true && data.hold === true) {
                    const reason = data.reason || "Input kurang presisi";
                    output.parts.unshift({ type: "text", text: `[HOLD] ${reason}\n` });
                    return;
                }

                // BLOCKED — permission denied
                if (data.blocked === true && !data.hold) {
                    const reason = data.reason || "Intent diblokir oleh work mode";
                    output.parts.unshift({ type: "text", text: `[BLOCKED] ${reason}\n` });
                    return;
                }

                // Build footer
                const project = data.project || "farewell-assistant";
                const projectCode = data.project_code || "";
                const projectLabel = projectCode ? `${projectCode}-${project}` : project;
                const workMode = (data.work_mode || "build").toUpperCase();
                const turn = data.turn || 0;
                const chainLen = Array.isArray(data.chain) ? data.chain.length : 0;
                const confidence = data.confidence ? Math.round(data.confidence * 100) + "%" : "-";
                const llmMode = data.llm_mode || "Online";
                const llmModel = data.model_primary || "qwen3.5-0.8b";

                const footer = `Farewell: ON | Project: ${projectLabel} | ${workMode} | Turn: ${turn} | Chain: ${chainLen} | ${confidence} | LLM:${llmMode}\n`;

                // Prepend warnings and metadata
                const parts = [{ type: "text", text: footer }];
                if (data.task_warning) {
                    parts.push({ type: "text", text: `⚠️ ${data.task_warning}\n` });
                }
                if (Array.isArray(data.secondary_intents) && data.secondary_intents.length > 0) {
                    parts.push({ type: "text", text: `⚠️ Multi-intent terdeteksi: intent utama=[${data.intent}], intent tambahan=[${data.secondary_intents.join(", ")}]. Intent tambahan tidak dijalankan dalam chain ini.\n` });
                }
                if (Array.isArray(data.post_steps) && data.post_steps.length > 0) {
                    parts.push({ type: "text", text: `📋 Post-steps: ${data.post_steps.join(" → ")} — jalankan setelah chain selesai.\n` });
                }
                if (data.degraded) {
                    parts.push({ type: "text", text: `⚠️ Chain degraded: ${data.degraded}\n` });
                }

                // Dynamic project context injection
                if (data.project) {
                    const contextFile = path.join(ctx.directory, "data", "context", `${data.project}.md`);
                    if (fs.existsSync(contextFile)) {
                        const ctxContent = fs.readFileSync(contextFile, "utf-8").trim();
                        if (ctxContent) {
                            parts.push({ type: "text", text: `\n--- Project Context (${data.project}) ---\n${ctxContent}\n--- End Project Context ---\n` });
                        }
                    }
                }

                output.parts.unshift(...parts);
            } catch (e) {
                logError(`Unhandled plugin error: ${e.message || e}`);
                try {
                    output.parts.unshift({ type: "text", text: `[PIPELINE ERROR] ${e.message || "Unknown error"}\n` });
                } catch (_) {}
            }
        },
    };
};

function findPython(projectDir) {
    const candidates = ["py", "python3", "python"];
    const venvWin = path.join(projectDir, ".venv", "Scripts", "python.exe");
    const venvUnix = path.join(projectDir, ".venv", "bin", "python3");
    if (fs.existsSync(venvWin)) return venvWin;
    if (fs.existsSync(venvUnix)) return venvUnix;
    return candidates[0];
}

function extractText(parts) {
    if (!Array.isArray(parts)) return "";
    for (const part of parts) {
        if (part && part.type === "text" && part.text) return part.text.trim();
    }
    return "";
}
