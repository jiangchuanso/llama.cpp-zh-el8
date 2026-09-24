<script lang="ts">
	import { parseReadFileMeta } from './parsers/read-file';
	import ToolCallBlock from './ToolCallBlock.svelte';
	import { SyntaxHighlightedCode } from '$lib/components/app';
	import { CODE_BLOCK, MAX_HEIGHT_CODE_BLOCK } from '$lib/constants';
	import { t } from '$lib/i18n';
	import type { AgenticSection } from '$lib/types';

	interface Props {
		section: AgenticSection;
		open: boolean;
		isStreaming: boolean;
		onToggle?: () => void;
	}

	let { isStreaming, onToggle, open, section }: Props = $props();

	const readFileMeta = $derived(parseReadFileMeta(section));
</script>

<ToolCallBlock {isStreaming} meta={readFileMeta} {onToggle} {open} {section}>
	{#snippet titleSnippet()}
		<span class="flex min-w-0 flex-wrap items-baseline gap-x-1">
			<span class="shrink-0 text-muted-foreground">{t('Read file')}</span>

			<span class="flex min-w-0 items-baseline gap-1.5">
				<span class="min-w-0 overflow-x-auto font-mono">{readFileMeta?.fileName}</span>

				{#if readFileMeta?.lineRange}
					<span class="shrink-0 text-muted-foreground">
						{t('(lines {start}-{end})', {
							end: readFileMeta.lineRange.end,
							start: readFileMeta.lineRange.start
						})}
					</span>
				{/if}
			</span>
		</span>
	{/snippet}

	{#snippet children(_meta, _ctx)}
		{#if section.toolResult}
			<SyntaxHighlightedCode
				code={section.toolResult}
				language={readFileMeta?.language ?? CODE_BLOCK.DEFAULT_LANGUAGE}
				maxHeight={MAX_HEIGHT_CODE_BLOCK}
			/>
		{:else}
			<div class="rounded bg-muted/20 p-2 text-xs text-muted-foreground/70 italic">
				{t('Waiting for file content...')}
			</div>
		{/if}
	{/snippet}
</ToolCallBlock>
