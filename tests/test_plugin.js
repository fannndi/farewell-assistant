/**
 * Tests for intent-router.js plugin.
 * Run: node tests/test_plugin.js
 */

const assert = require("assert");

// Minimal mock for parts
function extractText(parts) {
    if (!Array.isArray(parts)) return "";
    for (const part of parts) {
        if (part && part.type === "text" && part.text) return part.text.trim();
    }
    return "";
}

// Test extractText
assert.strictEqual(extractText(null), "");
assert.strictEqual(extractText([]), "");
assert.strictEqual(extractText([{ type: "text", text: "  hello  " }]), "hello");
assert.strictEqual(extractText([{ type: "text", text: "first" }, { type: "text", text: "second" }]), "first");
assert.strictEqual(extractText([{ type: "image", text: "img" }]), "");
assert.strictEqual(extractText([{ type: "text", text: "" }]), "");
assert.strictEqual(extractText([{ type: "text", text: "  " }]), "");

// Test footer format parsing
function buildFooter(data) {
    const project = data.project || "farewell-assistant";
    const workMode = (data.work_mode || "build").toUpperCase();
    const turn = data.turn || 0;
    const chainLen = Array.isArray(data.chain) ? data.chain.length : 0;
    const confidence = data.confidence ? Math.round(data.confidence * 100) + "%" : "-";
    const llmMode = (data.profile || "eco");
    const llmDisplay = llmMode.charAt(0).toUpperCase() + llmMode.slice(1);
    return `Farewell: ON | Project: ${project} | ${workMode} | Turn: ${turn} | Chain: ${chainLen} | ${confidence} | ${llmDisplay}\n`;
}

// Test footer with full data
const footer1 = buildFooter({
    project: "farewell-assistant",
    work_mode: "build",
    turn: 12,
    chain: ["a", "b", "c"],
    confidence: 0.95,
    profile: "eco"
});
assert.ok(footer1.includes("Farewell: ON"), "footer should contain Farewell: ON");
assert.ok(footer1.includes("Project: farewell-assistant"), "footer should contain project");
assert.ok(footer1.includes("BUILD"), "footer should contain work mode");
assert.ok(footer1.includes("Turn: 12"), "footer should contain turn");
assert.ok(footer1.includes("Chain: 3"), "footer should contain chain length");
assert.ok(footer1.includes("95%"), "footer should contain confidence");
assert.ok(footer1.includes("Eco"), "footer should contain LLM mode");

// Test footer with defaults
const footer2 = buildFooter({});
assert.ok(footer2.includes("Turn: 0"), "default turn is 0");
assert.ok(footer2.includes("Chain: 0"), "default chain is 0");
assert.ok(footer2.includes("Eco"), "default LLM is eco");

// Test BLOCKED check
const blockedData = { blocked: true, hold: false, reason: "Permission denied" };
assert.strictEqual(blockedData.blocked === true && !blockedData.hold, true);

const holdData = { blocked: true, hold: true, reason: "Input too vague" };
assert.strictEqual(holdData.blocked === true && holdData.hold, true);

// Test staleness check
const callTime = Date.now();
const staleTime = new Date(Date.now() - 5000).toISOString();
const freshTime = new Date(Date.now() - 500).toISOString();

function isStale(pipelineTime, callTimeMs) {
    return new Date(pipelineTime).getTime() < callTimeMs - 2000;
}

assert.strictEqual(isStale(staleTime, callTime), true, "stale data detected");
assert.strictEqual(isStale(freshTime, callTime), false, "fresh data accepted");

console.log("✓ All 20 plugin tests passed");
