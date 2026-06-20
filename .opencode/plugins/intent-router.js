// Run precision pipeline on every user message.
// Blocking: waits for pipeline to complete (PIPELINE_TIMEOUT env or 15s default).
// Prepend pipeline result as [Pipeline:] prefix to user message parts.
// AI sees intent, complexity, confidence, and skill chain before every turn.

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

const PIPELINE_TIMEOUT = parseInt(process.env.PIPELINE_TIMEOUT || "15000", 10);

exports.server = async (ctx) => {
    return {
        "chat.message": async (_input, output) => {
            try {
                const text = extractText(output?.parts);
                if (!text || text.length < 3) return;

                // Run pipeline and wait for result
                const scriptPath = path.join(ctx.directory, "scripts", "run-router.ps1");
                const escaped = text.replace(/"/g, '`"');
                execSync(
                    `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}" -InputText "${escaped}"`,
                    { timeout: PIPELINE_TIMEOUT, windowsHide: true, stdio: "ignore" }
                );

                // Read fresh pipeline result
                const pipelinePath = path.join(ctx.directory, ".opencode", "pipeline-result.json");
                if (!fs.existsSync(pipelinePath)) return;
                const raw = fs.readFileSync(pipelinePath, "utf-8").replace(/^\uFEFF/, "");
                const data = JSON.parse(raw);
                if (!data || !data.intent) return;

                // Check for HOLD — input too vague
                if (data.blocked === true && data.hold === true) {
                    const reason = data.reason || "Input kurang presisi";
                    const prefix = `[HOLD] ${reason}\n`;
                    output.parts.unshift({ type: "text", text: prefix });
                    return;
                }

                // Build footer — single consistent format
                const intent = data.intent || "unknown";
                const domain = data.domain || "";
                const complexity = data.complexity || "";
                const confidence = data.confidence ? Math.round(data.confidence * 100) + "%" : "";
                const chain = data.chain || [];
                const chainSteps = chain.length > 0 ? chain.length : "";
                const model = data.model_primary || "";
                const turn = data.turn || "";
                const work = data.work_mode || "";
                const mode = data.profile || "";

                const footer = `Intent: ${intent} | Complexity: ${complexity} (${confidence}) | Domain: ${domain} | Chain: ${chainSteps} steps | Model: ${model} | Work: ${work} | Turn: ${turn} | Mode: ${mode}\n`;

                // Prepend to user message — AI sees this before the actual input
                output.parts.unshift({ type: "text", text: footer });
            } catch (e) {
                // Log error but never crash the chat
                console.error("[intent-router] pipeline error:", e.message || e);
            }
        },
    };
};

function extractText(parts) {
    if (!Array.isArray(parts)) return "";
    for (const part of parts) {
        if (part && part.type === "text" && part.text) return part.text.trim();
    }
    return "";
}
