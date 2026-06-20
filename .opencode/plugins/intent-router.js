// Run precision pipeline on every user message.
// Blocking: waits for pipeline to complete (PIPELINE_TIMEOUT env or 15s default).
// Prepend footer to user message parts — project awareness + pipeline status.
//
// Security: User input passed as separate argv arg, NOT interpolated into shell command.

const { execFileSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const PIPELINE_TIMEOUT = parseInt(process.env.PIPELINE_TIMEOUT || "30000", 10);

exports.server = async (ctx) => {
    return {
        "chat.message": async (_input, output) => {
            try {
                const text = extractText(output?.parts);
                if (!text || text.length < 3) return;

                const py = findPython(ctx.directory);
                const callTime = Date.now();

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
                    // Timeout or non-zero exit
                }

                const pipelinePath = path.join(ctx.directory, ".opencode", "pipeline-result.json");
                if (!fs.existsSync(pipelinePath)) return;
                const raw = fs.readFileSync(pipelinePath, "utf-8").replace(/^\uFEFF/, "");
                const data = JSON.parse(raw);
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
                const workMode = (data.work_mode || "build").toUpperCase();
                const turn = data.turn || 0;
                const chainLen = Array.isArray(data.chain) ? data.chain.length : 0;
                const confidence = data.confidence ? Math.round(data.confidence * 100) + "%" : "-";
                const llmMode = (data.profile || "eco");
                const llmDisplay = llmMode.charAt(0).toUpperCase() + llmMode.slice(1);

                const footer = `Farewell: ON | Project: ${project} | ${workMode} | Turn: ${turn} | Chain: ${chainLen} | ${confidence} | ${llmDisplay}\n`;

                output.parts.unshift({ type: "text", text: footer });
            } catch (e) {
                console.error("[intent-router] pipeline error:", e.message || e);
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
