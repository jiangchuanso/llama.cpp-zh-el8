<script lang="ts">
	import ContextGaugeDetailRow from './ContextGaugeDetailRow.svelte';
	import { gaugePopup } from './gauge-popup.svelte';
	import { ChevronDown } from '@lucide/svelte';
	import * as Collapsible from '$lib/components/ui/collapsible';
	import { STATS_UNITS } from '$lib/constants';
	import { t } from '$lib/i18n';

	interface Props {
		currentRead: number;
		currentFresh: number;
		currentCache: number;
		currentOutput: number;
		kvTotal: number;
		cumulativeRead: number;
		cumulativeOutput: number;
		cumulativeCacheTotal: number;
		averageTokensPerSecond: number | null;
		transientDetails: string[];
	}

	let {
		averageTokensPerSecond,
		cumulativeCacheTotal,
		cumulativeOutput,
		cumulativeRead,
		currentCache,
		currentFresh,
		currentOutput,
		currentRead,
		kvTotal,
		transientDetails
	}: Props = $props();

	const hasCumulative = $derived(cumulativeRead > 0 || cumulativeOutput > 0);
	const hasCurrent = $derived(currentRead > 0 || currentOutput > 0);
</script>

<Collapsible.Root bind:open={gaugePopup.detailsOpen} class="mt-3 border-t border-border/50 pt-4">
	<Collapsible.Trigger
		class="flex w-full cursor-pointer items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
	>
		<span>{t('Token usage details')}</span>

		<ChevronDown
			class={'ml-auto h-3 w-3 transition-transform' + (gaugePopup.detailsOpen ? ' rotate-180' : '')}
		/>
	</Collapsible.Trigger>

	<Collapsible.Content class="flex flex-col gap-4 text-xs pt-4">
		{#if hasCumulative}
			<div>
				<h3 class="text-[11px] font-medium uppercase tracking-wide text-muted-foreground/70 mb-2">
					{t('Across all turns')}
				</h3>

				<div class="flex flex-col gap-2">
					{#if cumulativeRead > 0}
						<ContextGaugeDetailRow
							label={t('Prompt tokens evaluated')}
							subtitle={cumulativeCacheTotal > 0
								? t('{value} reused from KV cache', {
										value: cumulativeCacheTotal.toLocaleString()
									})
								: undefined}
							value={t('{value} tok', { value: cumulativeRead.toLocaleString() })}
						/>
					{/if}

					{#if cumulativeOutput > 0}
						<ContextGaugeDetailRow
							label={t('Tokens generated')}
							value={t('{value} tok', { value: cumulativeOutput.toLocaleString() })}
						/>
					{/if}
				</div>
			</div>
		{/if}

		{#if hasCurrent}
			<div>
				<h3 class="text-[11px] font-medium uppercase tracking-wide text-muted-foreground/70 mb-2">
					{t('This turn · KV cache')}
				</h3>

				<div class="flex flex-col gap-2">
					{#if currentRead > 0}
						<ContextGaugeDetailRow
							label={t('Prompt')}
							subtitle={currentCache > 0
								? t('{fresh} fresh + {cached} cached', {
										cached: currentCache.toLocaleString(),
										fresh: currentFresh.toLocaleString()
									})
								: undefined}
							value={t('{value} tok', { value: currentRead.toLocaleString() })}
						/>
					{/if}

					{#if currentOutput > 0}
						<ContextGaugeDetailRow
							label={t('Generated')}
							value={t('{value} tok', { value: currentOutput.toLocaleString() })}
						/>
					{/if}

					<div class="pt-1 mt-0.5 border-t border-border/30">
						<div class="flex justify-between">
							<span class="text-muted-foreground">{t('KV cache total')}</span>

							<span class="font-mono font-medium"
								>{t('{value} tok', { value: kvTotal.toLocaleString() })}</span
							>
						</div>
					</div>
				</div>
			</div>
		{/if}

		{#if averageTokensPerSecond !== null}
			<div class="pt-1.5 mt-1 border-t border-border/30">
				<ContextGaugeDetailRow
					label={t('Avg speed')}
					value={`${averageTokensPerSecond.toFixed(1)}${STATS_UNITS.TOKENS_PER_SECOND}`}
				/>
			</div>
		{/if}

		{#each transientDetails as detail (detail)}
			<div class="font-mono text-muted-foreground">{detail}</div>
		{/each}
	</Collapsible.Content>
</Collapsible.Root>
