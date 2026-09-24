<script lang="ts">
	import { ChevronLeft, ChevronRight } from '@lucide/svelte';
	import { ActionIcon } from '$lib/components/app';
	import { getChatMessageActionsContext } from '$lib/contexts';
	import { t } from '$lib/i18n';

	interface Props {
		class?: string;
	}

	let { class: className = '' }: Props = $props();

	const messageActions = getChatMessageActionsContext();

	let siblingInfo = $derived(messageActions.siblingInfo);

	let hasPrevious = $derived(siblingInfo && siblingInfo.currentIndex > 0);
	let hasNext = $derived(siblingInfo && siblingInfo.currentIndex < siblingInfo.totalSiblings - 1);
	let nextSiblingId = $derived(
		hasNext ? siblingInfo!.siblingIds[siblingInfo!.currentIndex + 1] : null
	);
	let previousSiblingId = $derived(
		hasPrevious ? siblingInfo!.siblingIds[siblingInfo!.currentIndex - 1] : null
	);
</script>

{#if siblingInfo && siblingInfo.totalSiblings > 1}
	<div
		aria-label={t('Message version {current} of {total}', {
			current: siblingInfo.currentIndex + 1,
			total: siblingInfo.totalSiblings
		})}
		class="flex items-center gap-1 text-xs text-muted-foreground {className}"
		role="navigation"
	>
		<ActionIcon
			class="h-5 w-5 p-0 {!hasPrevious ? '!cursor-not-allowed opacity-30' : ''}"
			disabled={!hasPrevious}
			icon={ChevronLeft}
			onclick={() => messageActions.navigateToSibling(previousSiblingId!)}
			tooltip={t('Previous version')}
		/>

		<span class="px-1 font-mono text-xs">
			{siblingInfo.currentIndex + 1}/{siblingInfo.totalSiblings}
		</span>

		<ActionIcon
			class="h-5 w-5 p-0 {!hasNext ? 'opacity-30' : ''}"
			disabled={!hasNext}
			icon={ChevronRight}
			onclick={() => messageActions.navigateToSibling(nextSiblingId!)}
			tooltip={t('Next version')}
		/>
	</div>
{/if}
