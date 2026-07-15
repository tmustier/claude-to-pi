import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import {
	CONFIG_DIR_NAME,
	DEFAULT_COMPACTION_SETTINGS,
	estimateTokens,
	findCutPoint,
	generateSummary,
	getAgentDir,
	type ContextEvent,
	type ExtensionAPI,
	type ExtensionContext,
	type SessionEntry,
} from "@earendil-works/pi-coding-agent";

/**
 * Soft context compaction for long-running Claude model tool loops.
 *
 * This extension does not call ctx.compact() in the middle of an active turn.
 * Instead, it uses Pi's public `context` hook to replace the exact outgoing
 * message list for the next provider request with:
 *
 *   compactionSummary + recent suffix
 *
 * The agent loop then continues naturally after a tool result. This gives Claude
 * sessions the user-visible behavior of "auto-compact then continue" without
 * aborting the active run or relying on context-overflow retry behavior. Ordinary
 * post-run compaction still belongs to the configured Pi compaction package/policy.
 */

type AgentMessage = Parameters<typeof estimateTokens>[0];
type ModelRef = `${string}/${string}`;

type SoftCompactionConfig = {
	enabled: boolean;
	thresholdTokens: number;
	keepRecentTokens: number;
	reserveTokens: number;
	modelPatterns: string[];
	summaryModel?: string;
	status: boolean;
	notify: boolean;
};

type SummaryCache = {
	modelRef: string;
	summaryModelRef: string;
	coveredEnd: number;
	sourceSignature: string;
	summary: string;
	tokensBefore: number;
};

const DEFAULT_CONFIG: SoftCompactionConfig = {
	enabled: true,
	thresholdTokens: 200_000,
	keepRecentTokens: DEFAULT_COMPACTION_SETTINGS.keepRecentTokens,
	reserveTokens: DEFAULT_COMPACTION_SETTINGS.reserveTokens,
	modelPatterns: [
		"anthropic/claude-fable-*",
		"anthropic/claude-opus-*",
		"anthropic/claude-sonnet-*",
		"*/claude-fable-*",
		"*/claude-opus-*",
		"*/claude-sonnet-*",
	],
	status: true,
	notify: true,
};

const CONFIG_FILE = "soft-context-compaction.json";
const STATUS_KEY = "soft-context-compaction";
const DEDUPE_RESET_MS = 5 * 60_000;

const POST_RUN_THRESHOLDS_BY_MODEL: Record<string, number> = {
	"anthropic/claude-fable-5": 120_000,
	"anthropic/claude-opus-4-8": 120_000,
	"anthropic/claude-sonnet-4-6": 120_000,
	"openai-codex/gpt-5.6-sol": 120_000,
	"openai-codex/gpt-5.3-codex": 120_000,
};

const POST_RUN_COOLDOWN_MS = 60_000;
const DEFAULT_MAX_COMPACTION_ATTEMPTS = 3;
const DEFAULT_COMPACTION_RETRY_BASE_DELAY_MS = 5_000;
const DEFAULT_COMPACTION_RETRY_MAX_DELAY_MS = 30_000;

type NotifyLevel = "info" | "warning" | "error";

function configuredPositiveInteger(name: string, fallback: number): number {
	const raw = process.env[name];
	if (!raw) return fallback;
	const parsed = Number.parseInt(raw, 10);
	return Number.isFinite(parsed) && parsed > 0 ? parsed : fallback;
}

function configuredNonNegativeInteger(name: string, fallback: number): number {
	const raw = process.env[name];
	if (!raw) return fallback;
	const parsed = Number.parseInt(raw, 10);
	return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function notifyPostRun(ctx: ExtensionContext, message: string, level: NotifyLevel = "info"): void {
	try {
		if (!ctx.hasUI) return;
		ctx.ui.notify(message, level);
	} catch {
		// Ignore stale extension contexts.
	}
}

function normalizeError(error: unknown): string {
	return String(error instanceof Error ? error.message : error ?? "")
		.trim()
		.toLowerCase()
		.replace(/^error\s*:\s*/, "")
		.trim();
}

function isTransientProviderError(error: unknown): boolean {
	const normalized = normalizeError(error);
	if (!normalized) return false;

	if (
		/usage_limit_reached|chatgpt usage limit|context_length_exceeded|no api key|invalid authentication|forbidden|insufficient permissions|missing scopes|workspace admin|quota/i.test(
			normalized,
		)
	) {
		return false;
	}

	return /overloaded|server_is_overloaded|service_unavailable|service unavailable|server_error|server error|internal server error|api_error|rate.?limit|too many requests|429|500|502|503|504|network.?error|connection.?error|connection.?lost|websocket.?error|websocket.?closed|fetch failed|socket hang up|other side closed|ended without|http2 request did not get a response|timed? out|timeout|terminated|retry delay/i.test(
		normalized,
	);
}

function delayForAttempt(attempt: number, baseDelayMs: number, maxDelayMs: number): number {
	const exponential = baseDelayMs * 2 ** Math.max(0, attempt - 1);
	return Math.min(exponential, maxDelayMs);
}


function isRecord(value: unknown): value is Record<string, unknown> {
	return typeof value === "object" && value !== null && !Array.isArray(value);
}

function positiveInteger(value: unknown, fallback: number): number {
	return typeof value === "number" && Number.isFinite(value) && value > 0 ? Math.floor(value) : fallback;
}

function booleanValue(value: unknown, fallback: boolean): boolean {
	return typeof value === "boolean" ? value : fallback;
}

function stringArray(value: unknown, fallback: string[]): string[] {
	if (!Array.isArray(value)) return fallback;
	const strings = value.filter((item): item is string => typeof item === "string" && item.trim().length > 0);
	return strings.length > 0 ? strings : fallback;
}

function stringValue(value: unknown, fallback: string | undefined): string | undefined {
	return typeof value === "string" && value.trim().length > 0 ? value.trim() : fallback;
}

function normalizeConfigPatch(value: unknown, base: SoftCompactionConfig): SoftCompactionConfig {
	if (!isRecord(value)) return base;
	return {
		enabled: booleanValue(value.enabled, base.enabled),
		thresholdTokens: positiveInteger(value.thresholdTokens, base.thresholdTokens),
		keepRecentTokens: positiveInteger(value.keepRecentTokens, base.keepRecentTokens),
		reserveTokens: positiveInteger(value.reserveTokens, base.reserveTokens),
		modelPatterns: stringArray(value.modelPatterns, base.modelPatterns),
		summaryModel: stringValue(value.summaryModel, base.summaryModel),
		status: booleanValue(value.status, base.status),
		notify: booleanValue(value.notify, base.notify),
	};
}

function readJsonPatch(path: string): unknown | undefined {
	if (!existsSync(path)) return undefined;
	return JSON.parse(readFileSync(path, "utf8"));
}

function loadConfig(ctx: ExtensionContext): SoftCompactionConfig {
	let config = DEFAULT_CONFIG;

	const globalPatch = readJsonPatch(join(getAgentDir(), CONFIG_FILE));
	config = normalizeConfigPatch(globalPatch, config);

	// Project config is trusted-project-only. Global/user config above always applies.
	if (ctx.isProjectTrusted()) {
		const projectPatch = readJsonPatch(join(ctx.cwd, CONFIG_DIR_NAME, CONFIG_FILE));
		config = normalizeConfigPatch(projectPatch, config);
	}

	return config;
}

function currentModelRef(ctx: ExtensionContext): ModelRef | undefined {
	if (!ctx.model) return undefined;
	return `${ctx.model.provider}/${ctx.model.id}`;
}

function wildcardToRegExp(pattern: string): RegExp {
	const escaped = pattern.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
	return new RegExp(`^${escaped}$`);
}

function modelMatches(modelRef: string, patterns: string[]): boolean {
	return patterns.some((pattern) => wildcardToRegExp(pattern).test(modelRef));
}

function estimateTextTokens(text: string | undefined): number {
	return text ? Math.ceil(text.length / 4) : 0;
}

function estimateRawContextTokens(messages: AgentMessage[], ctx: ExtensionContext): number {
	let tokens = estimateTextTokens(ctx.getSystemPrompt());
	for (const message of messages) {
		tokens += estimateTokens(message);
	}
	return tokens;
}

function messageHash(input: string): string {
	let hash = 5381;
	for (let i = 0; i < input.length; i++) {
		hash = ((hash << 5) + hash) ^ input.charCodeAt(i);
	}
	return (hash >>> 0).toString(36);
}

function messageSignature(message: AgentMessage, index: number): string {
	const role = (message as { role?: unknown }).role ?? "?";
	const timestamp = (message as { timestamp?: unknown }).timestamp ?? "?";
	return `${index}:${String(role)}:${String(timestamp)}:${estimateTokens(message)}:${messageHash(JSON.stringify(message))}`;
}

function rangeSignature(messages: AgentMessage[], endExclusive: number): string {
	if (endExclusive <= 0) return "0:empty";
	return [
		String(endExclusive),
		messageSignature(messages[0], 0),
		messageSignature(messages[endExclusive - 1], endExclusive - 1),
	].join("|");
}

function fakeEntriesFor(messages: AgentMessage[]): SessionEntry[] {
	return messages.map((message, index) => ({
		type: "message",
		id: `soft-context-${index}`,
		parentId: index === 0 ? undefined : `soft-context-${index - 1}`,
		timestamp: (message as { timestamp?: number }).timestamp ?? Date.now(),
		message,
	})) as unknown as SessionEntry[];
}

function chooseCutIndex(messages: AgentMessage[], keepRecentTokens: number): number | undefined {
	if (messages.length === 0) return undefined;
	const entries = fakeEntriesFor(messages);
	const cut = findCutPoint(entries, 0, entries.length, keepRecentTokens);
	if (cut.firstKeptEntryIndex <= 0 || cut.firstKeptEntryIndex >= messages.length) return undefined;
	return cut.firstKeptEntryIndex;
}

function createSummaryMessage(summary: string, tokensBefore: number): AgentMessage {
	return {
		role: "compactionSummary",
		summary,
		tokensBefore,
		timestamp: Date.now(),
	} as AgentMessage;
}

function parseModelRef(ref: string): { provider: string; id: string } | undefined {
	const slash = ref.indexOf("/");
	if (slash <= 0 || slash === ref.length - 1) return undefined;
	return { provider: ref.slice(0, slash), id: ref.slice(slash + 1) };
}

function formatTokens(tokens: number): string {
	return tokens.toLocaleString("en-US");
}

function safeNotify(ctx: ExtensionContext, config: SoftCompactionConfig, message: string, level: "info" | "warning" | "error" = "info") {
	if (!config.notify) return;
	try {
		if (ctx.hasUI) ctx.ui.notify(message, level);
	} catch {
		// Stale extension contexts can throw from async callbacks; notifications must not crash Pi.
	}
}

function safeStatus(ctx: ExtensionContext, config: SoftCompactionConfig, message: string | undefined) {
	if (!config.status) return;
	try {
		if (ctx.hasUI) ctx.ui.setStatus(STATUS_KEY, message);
	} catch {
		// Ignore stale UI contexts.
	}
}

export default function modelCompactionTrigger(pi: ExtensionAPI) {
	const maxAttempts = configuredPositiveInteger(
		"PI_MODEL_COMPACTION_MAX_ATTEMPTS",
		DEFAULT_MAX_COMPACTION_ATTEMPTS,
	);
	const baseDelayMs = configuredNonNegativeInteger(
		"PI_MODEL_COMPACTION_RETRY_BASE_DELAY_MS",
		DEFAULT_COMPACTION_RETRY_BASE_DELAY_MS,
	);
	const maxDelayMs = configuredNonNegativeInteger(
		"PI_MODEL_COMPACTION_RETRY_MAX_DELAY_MS",
		DEFAULT_COMPACTION_RETRY_MAX_DELAY_MS,
	);

	let config: SoftCompactionConfig = DEFAULT_CONFIG;
	let cache: SummaryCache | undefined;
	let inFlight = false;
	let lastWarningAt = new Map<string, number>();
	let previousPostRunTokens: number | null | undefined;
	let postRunInFlight = false;
	let lastPostRunTriggeredAt = 0;
	let retryTimer: ReturnType<typeof setTimeout> | undefined;

	function resetCache() {
		cache = undefined;
		inFlight = false;
	}

	function notifyOnce(ctx: ExtensionContext, key: string, message: string, level: "info" | "warning" | "error" = "warning") {
		const now = Date.now();
		const last = lastWarningAt.get(key) ?? 0;
		if (now - last < DEDUPE_RESET_MS) return;
		lastWarningAt.set(key, now);
		safeNotify(ctx, config, message, level);
	}


	function clearRetryTimer(): void {
		if (!retryTimer) return;
		clearTimeout(retryTimer);
		retryTimer = undefined;
	}

	function finishFailedAttempt(error: Error, wasTransient: boolean, ctx: ExtensionContext): void {
		postRunInFlight = false;
		clearRetryTimer();
		if (wasTransient) {
			// Let a later agent_end cross the threshold again after cooldown instead of getting stuck
			// above the threshold forever after one unlucky provider outage.
			previousPostRunTokens = null;
		}
		notifyPostRun(ctx, `Compaction failed: ${error.message}`, "error");
	}

	function runCompactionAttempt(
		ctx: ExtensionContext,
		modelRef: string,
		currentTokens: number,
		threshold: number,
		attempt: number,
	): void {
		postRunInFlight = true;
		lastPostRunTriggeredAt = Date.now();

		const attemptSuffix = maxAttempts > 1 ? ` (attempt ${attempt}/${maxAttempts})` : "";
		notifyPostRun(
			ctx,
			`Compacting ${modelRef} at ${currentTokens}/${threshold} tokens using Pi default compaction${attemptSuffix}`,
			"info",
		);

		try {
			ctx.compact({
				onComplete: () => {
					postRunInFlight = false;
					clearRetryTimer();
					previousPostRunTokens = null;
					notifyPostRun(ctx, "Compaction completed", "info");
				},
				onError: (error) => {
					const transient = isTransientProviderError(error);
					if (!transient || attempt >= maxAttempts) {
						finishFailedAttempt(error, transient, ctx);
						return;
					}

					const delayMs = delayForAttempt(attempt, baseDelayMs, maxDelayMs);
					notifyPostRun(
						ctx,
						`Compaction hit a transient provider error; retrying in ${Math.round(delayMs / 1000)}s (${attempt + 1}/${maxAttempts})`,
						"warning",
					);
					clearRetryTimer();
					retryTimer = setTimeout(() => {
						retryTimer = undefined;
						runCompactionAttempt(ctx, modelRef, currentTokens, threshold, attempt + 1);
					}, delayMs);
				},
			});
		} catch {
			postRunInFlight = false;
			clearRetryTimer();
			previousPostRunTokens = null;
		}
	}

	function triggerPostRunCompaction(ctx: ExtensionContext, modelRef: string, currentTokens: number, threshold: number): void {
		runCompactionAttempt(ctx, modelRef, currentTokens, threshold, 1);
	}

	async function resolveSummaryModel(ctx: ExtensionContext) {
		const sessionModel = ctx.model;
		if (!config.summaryModel) return sessionModel;
		const parsed = parseModelRef(config.summaryModel);
		if (!parsed) {
			notifyOnce(ctx, "bad-summary-model", `Invalid summaryModel ${config.summaryModel}; using current model.`);
			return sessionModel;
		}
		const model = ctx.modelRegistry.find(parsed.provider, parsed.id);
		if (!model) {
			notifyOnce(ctx, "missing-summary-model", `Summary model ${config.summaryModel} not found; using current model.`);
			return sessionModel;
		}
		return model;
	}

	async function buildSummary(
		messages: AgentMessage[],
		cutIndex: number,
		ctx: ExtensionContext,
		modelRef: string,
		tokensBefore: number,
	): Promise<SummaryCache | undefined> {
		const targetSignature = rangeSignature(messages, cutIndex);
		const summaryModel = await resolveSummaryModel(ctx);
		if (!summaryModel) return undefined;
		const summaryModelRef = `${summaryModel.provider}/${summaryModel.id}`;

		if (
			cache &&
			cache.modelRef === modelRef &&
			cache.summaryModelRef === summaryModelRef &&
			cache.sourceSignature === targetSignature
		) {
			return cache;
		}

		let startIndex = 0;
		let previousSummary: string | undefined;
		if (
			cache &&
			cache.modelRef === modelRef &&
			cache.summaryModelRef === summaryModelRef &&
			cache.coveredEnd <= cutIndex &&
			rangeSignature(messages, cache.coveredEnd) === cache.sourceSignature
		) {
			startIndex = cache.coveredEnd;
			previousSummary = cache.summary;
		}

		const messagesToSummarize = messages.slice(startIndex, cutIndex);
		if (messagesToSummarize.length === 0 && previousSummary) {
			cache = { modelRef, summaryModelRef, coveredEnd: cutIndex, sourceSignature: targetSignature, summary: previousSummary, tokensBefore };
			return cache;
		}
		if (messagesToSummarize.length === 0) return undefined;

		const auth = await ctx.modelRegistry.getApiKeyAndHeaders(summaryModel);
		if (!auth.ok) {
			notifyOnce(ctx, `auth:${summaryModelRef}`, `Soft context compaction auth failed for ${summaryModelRef}: ${auth.error}`);
			return undefined;
		}
		if (!auth.apiKey) {
			notifyOnce(ctx, `auth-empty:${summaryModelRef}`, `No API key available for soft context compaction model ${summaryModelRef}.`);
			return undefined;
		}

		const thinkingLevel = pi.getThinkingLevel?.();
		const summary = await generateSummary(
			messagesToSummarize,
			summaryModel,
			config.reserveTokens,
			auth.apiKey,
			auth.headers,
			ctx.signal,
			"Automatic soft mid-turn compaction. Preserve the user's active request, exact file paths, function names, command outputs, errors, decisions, and any state needed to understand the raw recent suffix that remains in context.",
			previousSummary,
			thinkingLevel && thinkingLevel !== "off" ? thinkingLevel : undefined,
			undefined,
			auth.env,
		);

		if (!summary.trim()) {
			notifyOnce(ctx, "empty-summary", "Soft context compaction produced an empty summary; sending full context instead.");
			return undefined;
		}

		cache = {
			modelRef,
			summaryModelRef,
			coveredEnd: cutIndex,
			sourceSignature: targetSignature,
			summary,
			tokensBefore,
		};
		return cache;
	}

	async function maybeCompactContext(event: ContextEvent, ctx: ExtensionContext) {
		if (!config.enabled) return;

		const modelRef = currentModelRef(ctx);
		if (!modelRef || !modelMatches(modelRef, config.modelPatterns)) {
			if (cache?.modelRef && cache.modelRef !== modelRef) resetCache();
			safeStatus(ctx, config, undefined);
			return;
		}

		const rawEstimate = estimateRawContextTokens(event.messages, ctx);
		const reportedUsage = ctx.getContextUsage()?.tokens ?? 0;
		const triggerTokens = cache ? rawEstimate : Math.max(rawEstimate, reportedUsage);
		const threshold = config.thresholdTokens;

		if (!cache && triggerTokens < threshold) {
			safeStatus(ctx, config, `softctx · ${formatTokens(triggerTokens)}/${formatTokens(threshold)}`);
			return;
		}
		if (inFlight) {
			notifyOnce(ctx, "in-flight", "Soft context compaction is already in flight; sending full context for this request.");
			return;
		}

		const cutIndex = chooseCutIndex(event.messages, config.keepRecentTokens);
		if (cutIndex === undefined) {
			notifyOnce(
				ctx,
				"no-cut",
				`Soft context compaction could not find a safe cut point above ${formatTokens(threshold)} tokens; sending full context.`,
			);
			return;
		}

		try {
			inFlight = true;
			safeStatus(ctx, config, `softctx · compacting ${formatTokens(triggerTokens)}→keep ${formatTokens(config.keepRecentTokens)}`);
			const summaryCache = await buildSummary(event.messages, cutIndex, ctx, modelRef, triggerTokens);
			if (!summaryCache) return;

			const compactedMessages = [createSummaryMessage(summaryCache.summary, summaryCache.tokensBefore), ...event.messages.slice(cutIndex)];
			const compactedEstimate = estimateRawContextTokens(compactedMessages, ctx);
			safeStatus(
				ctx,
				config,
				`softctx · ${formatTokens(triggerTokens)}→${formatTokens(compactedEstimate)} / ${formatTokens(threshold)}`,
			);
			return { messages: compactedMessages };
		} catch (error) {
			if (!ctx.signal?.aborted) {
				const message = error instanceof Error ? error.message : String(error);
				notifyOnce(ctx, "summary-error", `Soft context compaction failed: ${message}`, "error");
			}
			return;
		} finally {
			inFlight = false;
		}
	}

	pi.on("session_start", async (_event, ctx) => {
		resetCache();
		lastWarningAt = new Map();
		try {
			config = loadConfig(ctx);
		} catch (error) {
			config = DEFAULT_CONFIG;
			const message = error instanceof Error ? error.message : String(error);
			safeNotify(ctx, config, `Failed to load ${CONFIG_FILE}: ${message}; using defaults.`, "warning");
		}
		if (config.enabled && config.status) {
			safeStatus(ctx, config, `softctx · ready @ ${formatTokens(config.thresholdTokens)}`);
		}
	});

	pi.on("context", maybeCompactContext);

	pi.on("agent_end", async (_event, ctx) => {
		const modelRef = currentModelRef(ctx);
		if (!modelRef) return;

		const threshold = POST_RUN_THRESHOLDS_BY_MODEL[modelRef];
		if (!threshold) return;

		const currentTokens = ctx.getContextUsage()?.tokens ?? null;
		if (currentTokens === null) return;

		try {
			ctx.ui.setStatus("model-compaction-trigger", `compact @ ${threshold.toLocaleString()}`);
		} catch {
			// Ignore stale UI contexts.
		}

		const crossedThreshold = previousPostRunTokens === undefined || previousPostRunTokens === null || previousPostRunTokens < threshold;
		previousPostRunTokens = currentTokens;

		if (!crossedThreshold || currentTokens < threshold) return;
		if (postRunInFlight) return;
		if (Date.now() - lastPostRunTriggeredAt < POST_RUN_COOLDOWN_MS) return;

		triggerPostRunCompaction(ctx, modelRef, currentTokens, threshold);
	});

	pi.on("session_compact", async () => resetCache());
	pi.on("session_tree", async () => resetCache());
	pi.on("model_select", async () => {
		previousPostRunTokens = undefined;
		resetCache();
	});
	pi.on("session_shutdown", async () => {
		clearRetryTimer();
		postRunInFlight = false;
		resetCache();
	});

	pi.registerCommand("soft-compact-status", {
		description: "Show soft context compaction config and cache status",
		handler: async (_args, ctx) => {
			config = loadConfig(ctx);
			const modelRef = currentModelRef(ctx) ?? "none";
			const active = modelRef !== "none" && modelMatches(modelRef, config.modelPatterns);
			ctx.ui.notify(
				[
					`Soft context compaction: ${config.enabled ? "enabled" : "disabled"}`,
					`model: ${modelRef} (${active ? "matched" : "not matched"})`,
					`thresholdTokens: ${formatTokens(config.thresholdTokens)}`,
					`keepRecentTokens: ${formatTokens(config.keepRecentTokens)}`,
					`summaryModel: ${config.summaryModel ?? "current model"}`,
					`cache: ${cache ? `${cache.coveredEnd} messages summarized with ${cache.summaryModelRef}` : "empty"}`,
				].join("\n"),
				"info",
			);
		},
	});

	pi.registerCommand("soft-compact-reset", {
		description: "Clear soft context compaction's in-memory summary cache",
		handler: async (_args, ctx) => {
			resetCache();
			safeNotify(ctx, config, "Soft context compaction cache cleared.", "info");
		},
	});
}
