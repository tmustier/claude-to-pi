/**
 * Pi Tips — shows a useful tip for non-technical users on each session start.
 *
 * Cycles through tips without repeating until all have been shown.
 * State is persisted in ~/.pi/agent/.tips-seen.json.
 */

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import * as fs from "node:fs";
import * as path from "node:path";
import * as os from "node:os";

const tips = [
	// ── Visualisation & documents ──────────────────────────────────
	{
		title: "Beautiful HTML pages",
		tip: 'Ask Pi to "create an HTML page showing…" — it can build interactive charts, dashboards, comparison tables, or timelines. Then type /open to view it in your browser.',
	},
	{
		title: "Slide decks from a prompt",
		tip: 'Say "make me a 5-slide deck about…" and Pi will generate a PowerPoint file. It can also edit existing .pptx files — just tell it what to change.',
	},
	{
		title: "Word docs & spreadsheets",
		tip: "Pi can create, read, and edit Word docs (.docx) and Excel spreadsheets (.xlsx). Try: \"create a one-pager about our product\" or \"make a spreadsheet comparing these options\".",
	},
	{
		title: "PDFs",
		tip: 'Pi can read PDFs, merge them, split them, extract text, and even OCR scanned documents. Just say "read this PDF" and drop a file path.',
	},

	// ── Email & comms ──────────────────────────────────────────────
	{
		title: "Email drafts",
		tip: 'Say "draft a follow-up email to [person] about [topic]" — Pi will write it, show you a preview, and wait for your OK before sending. You always get to review first.',
	},

	// ── Research & web ─────────────────────────────────────────────
	{
		title: "Web search",
		tip: 'Pi can search the web for you. Try: "find recent articles about [topic]" or "what\'s [company] doing lately?" — it returns real results, not training data.',
	},
	{
		title: "Read any webpage",
		tip: "Paste a URL and ask Pi to read it, summarize it, or answer questions about it. Works with articles, docs, even YouTube videos.",
	},

	// ── Pi is malleable ───────────────────────────────────────────
	{
		title: "Pi can extend itself",
		tip: "If you wish Pi could do something it can't, just ask: \"can you build me a tool that does X?\" Pi can create its own extensions, skills, and commands. You're not limited to what's installed.",
	},
	{
		title: "Make it yours",
		tip: "Don't like how something works? Say \"change how you do X\" or \"from now on, always Y\". Pi can update its own AGENTS.md, create new prompt templates, or build custom tools — right now, in this conversation.",
	},
	{
		title: "Automate your patterns",
		tip: "Catch yourself doing the same thing repeatedly? Tell Pi: \"I keep doing X — can you make that a command?\" It'll create a prompt template or extension so next time it's one step.",
	},
	{
		title: "There are no buttons",
		tip: "Pi isn't an app with fixed menus. It's more like a colleague who can learn new tricks. If you can describe what you want, Pi can probably do it — or build itself the ability to.",
	},
	{
		title: "Customise your setup",
		tip: "Everything in Pi is a text file you can change. Your AGENTS.md is your instruction manual for Pi. Your prompt templates are reusable workflows. Ask Pi to add to or change any of them.",
	},
	{
		title: "Build a workflow",
		tip: "Have a repeating process? Ask Pi to turn it into a prompt template. Then it's just /my-workflow.",
	},

	// ── Pi tips ────────────────────────────────────────────────────
	{
		title: "Cycle scoped models with Ctrl+P",
		tip: "Press Ctrl+P to cycle through your scoped model list. Use /scoped-models to choose which models appear and save the order.",
	},
	{
		title: "Change thinking level",
		tip: "Use Shift+Tab to cycle thinking level. Keep higher thinking for complex work; lower it for quick questions. /hotkeys shows the exact binding for your setup.",
	},
	{
		title: "The / command palette",
		tip: "Type / to see available commands. Useful ones from this setup include /onboard, /machine-doctor, /auto-pr, /bootstrap-from-claude-code, and /open.",
	},
	{
		title: "Be specific",
		tip: "The more context you give, the better the result. Instead of \"write an email\", try \"write a follow-up email to Sarah about the integration timeline we discussed yesterday\".",
	},
	{
		title: "Ask Pi to explain",
		tip: "If Pi does something you don't understand, just ask: \"what did you just do?\" or \"explain that in simple terms\". It'll walk you through it.",
	},
	{
		title: "Undo mistakes",
		tip: "If Pi makes a change you don't like, say \"undo that\" or \"revert that\". For git changes, Pi can reset to the previous state.",
	},
	{
		title: "Open anything",
		tip: "After Pi creates a file — a PDF, spreadsheet, HTML page, image — type /open to view it in the right app. Or /open with a path to open any file.",
	},
	{
		title: "Paste long text",
		tip: "You can paste multi-line content directly into Pi — email threads, documents, data. Pi handles it all. Use Shift+Enter if you need to type multiple lines yourself.",
	},
	{
		title: "Queue a follow-up",
		tip: "While Pi is working, Alt+Enter queues a follow-up that waits until all current work is done. Press Enter instead when you want to steer the active turn.",
	},
	{
		title: "Use the conversation tree",
		tip: "Type /tree, or press Esc twice while Pi is idle, to branch, fork, and move through previous points in the session without losing history.",
	},
	{
		title: "Name important sessions",
		tip: "Use /name <short-name> on important work. Later, /resume is much easier because you can find the session by name.",
	},
	{
		title: "Hot-reload changes",
		tip: "After Pi edits an extension, skill, prompt, or AGENTS.md, use /reload to load the new behaviour without starting a fresh session.",
	},
];

const STATE_FILE = path.join(os.homedir(), ".pi", "agent", ".tips-seen.json");

function loadSeen(): number[] {
	try {
		if (fs.existsSync(STATE_FILE)) {
			return JSON.parse(fs.readFileSync(STATE_FILE, "utf-8"));
		}
	} catch {
		// ignore
	}
	return [];
}

function saveSeen(seen: number[]): void {
	try {
		fs.writeFileSync(STATE_FILE, JSON.stringify(seen));
	} catch {
		// ignore
	}
}

function pickTip(): (typeof tips)[number] {
	let seen = loadSeen();

	if (seen.length >= tips.length) {
		seen = [];
	}

	const unseen = tips
		.map((t, i) => ({ tip: t, index: i }))
		.filter(({ index }) => !seen.includes(index));

	const pick = unseen[Math.floor(Math.random() * unseen.length)];

	seen.push(pick.index);
	saveSeen(seen);

	return pick.tip;
}

export default function (pi: ExtensionAPI) {
	pi.on("session_start", async (_event, ctx) => {
		const { title, tip } = pickTip();
		ctx.ui.notify(`💡 ${title}: ${tip}`, "info");
	});
}
