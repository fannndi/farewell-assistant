// Run precision pipeline on every user message.
// Non-blocking: never crashes or delays chat.
// Shells to scripts/run-router.ps1 which dot-sources all modules.

const { execSync } = require("child_process");
const path = require("path");

exports.server = async (ctx) => {
    return {
        "chat.message": async (_input, output) => {
            try {
                const text = extractText(output?.parts);
                if (!text || text.length < 3) return;

                const scriptPath = path.join(ctx.directory, ".", "scripts", "run-router.ps1");
                const escaped = text.replace(/"/g, '`"');
                execSync(
                    `powershell -NoProfile -ExecutionPolicy Bypass -File "${scriptPath}" -InputText "${escaped}"`,
                    { timeout: 30000, windowsHide: true, stdio: "ignore" }
                );
            } catch (_e) {
                // Non-blocking — never crash the chat
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
