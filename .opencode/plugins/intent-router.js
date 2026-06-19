// Run precision pipeline on every user message.
// Blocking: waits for pipeline to complete (15s timeout).
// Prepend pipeline result as [Pipeline:] prefix to user message parts.
// AI sees intent, complexity, confidence, and skill chain before every turn.

const { execSync } = require("child_process");
const path = require("path");
const fs = require("fs");

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
                    { timeout: 15000, windowsHide: true, stdio: "ignore" }
                );

                // Read fresh pipeline result
                const pipelinePath = path.join(ctx.directory, ".opencode", "pipeline-result.json");
                if (!fs.existsSync(pipelinePath)) return;
                const raw = fs.readFileSync(pipelinePath, "utf-8").replace(/^\uFEFF/, "");
                const data = JSON.parse(raw);
                if (!data || !data.intent) return;

                // Build compact prefix
                const intent = data.intent;
                const domain = data.domain || "";
                const complexity = data.complexity || "";
                const confidence = data.confidence ? Math.round(data.confidence * 100) + "%" : "";
                const chain = data.chain_summary || "";
                const source = data.source || "";

                const parts = [];
                if (intent) parts.push(intent);
                if (domain) parts.push(domain);
                if (complexity) parts.push(complexity);
                if (confidence) parts.push(confidence);
                if (source && source !== "structured") parts.push(source);

                const prefix = `[Pipeline: ${parts.join("/")} | ${chain}]\n`;

                // Prepend to user message — AI sees this before the actual input
                output.parts.unshift({ type: "text", text: prefix });
            } catch (_e) {
                // Never crash the chat
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
