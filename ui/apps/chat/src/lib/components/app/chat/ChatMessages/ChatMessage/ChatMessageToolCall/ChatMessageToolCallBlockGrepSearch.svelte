<script lang="ts">
	import { parseGrepSearchMeta } from './parsers/grep-search';
	import { t } from '#lib/i18n/index.ts';
	import ToolCallBlock from './ToolCallBlock.svelte';
	import { XCircle } from '@lucide/svelte';
	import { toolsStore } from '#lib/stores/index.ts';
	import type { AgenticSection } from '#lib/types/index.ts';
	import { abbreviateHome } from '#lib/utils/index.ts';

	interface Props {
		section: AgenticSection;
		open: boolean;
		isStreaming: boolean;
		onToggle?: () => void;
	}

	let { isStreaming, onToggle, open, section }: Props = $props();

	const grepMeta = $derived(parseGrepSearchMeta(section));
	const home = $derived(toolsStore.serverHome);
</script>

<ToolCallBlock {isStreaming} meta={grepMeta} {onToggle} {open} {section}>
	{#snippet titleSnippet(phrase)}
		{#if grepMeta}
			<span class="text-muted-foreground">{t(phrase.label)}&nbsp;</span>

			<span class="font-mono">{grepMeta.pattern}</span>

			<span class="text-muted-foreground">&nbsp;{t('in')}&nbsp;</span>

			<span class="font-mono" title={grepMeta.path}>{abbreviateHome(grepMeta.path, home)}</span>
		{/if}
	{/snippet}

	{#snippet children(meta, ctx)}
		{#if ctx.isPending}
			<div class="rounded bg-muted/20 p-2 text-caption text-muted-foreground/70 italic">
				{t('Searching...')}
			</div>
		{:else if meta?.errorMessage}
			<div
				class="flex items-start gap-2 rounded bg-surface-danger p-2 text-caption text-fg-danger italic"
			>
				<XCircle class="mt-0.5 size-icon-xs shrink-0" />

				<span>{meta.errorMessage}</span>
			</div>
		{:else if meta && meta.matches.length > 0}
			<div class="max-h-96 overflow-auto">
				{#each meta.matches as match, mi (mi)}
					<div class="font-mono text-caption leading-relaxed">
						<span class="text-muted-foreground/70">{match.file}</span>

						{#if meta.showLineNumbers && match.line != null}
							<span class="text-muted-foreground/70">:{match.line}</span>
						{/if}

						<span class="text-muted-foreground/70">:</span>

						<span>{match.content}</span>
					</div>
				{/each}
			</div>

			<div class="mt-1.5 text-caption text-muted-foreground/70 italic">
				{t('Total matches:')}
				<span class="font-mono">{meta.totalMatches ?? meta.matches.length}</span>

				{#if meta.showLineNumbers}
					&nbsp;<span class="italic">{t('(with line numbers)')}</span>
				{/if}
			</div>
		{:else}
			<div class="text-caption text-muted-foreground/70 italic">{t('No matches')}</div>

			<div class="mt-1.5 text-caption text-muted-foreground/70 italic">
				{t('Total matches:')} <span class="font-mono">{meta?.totalMatches ?? 0}</span>
			</div>
		{/if}
	{/snippet}
</ToolCallBlock>
