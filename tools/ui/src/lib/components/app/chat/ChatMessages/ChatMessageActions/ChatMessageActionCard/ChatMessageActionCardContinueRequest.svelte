<script lang="ts">
	import ChatMessageActionCard from './ChatMessageActionCard.svelte';
	import { RotateCw } from '@lucide/svelte';
	import { Button } from '$lib/components/ui/button';
	import { t } from '$lib/i18n';

	interface Props {
		onDecision: (shouldContinue: boolean) => void;
	}

	let { onDecision }: Props = $props();
</script>

<ChatMessageActionCard icon={RotateCw}>
	{#snippet message()}
		{t('Agentic turn limit reached. Continue?')}
	{/snippet}

	{#snippet actions()}
		<Button onclick={() => onDecision(true)} size="sm">{t('Continue')}</Button>

		<Button
			class="text-destructive hover:text-destructive"
			onclick={() => onDecision(false)}
			size="sm"
			variant="destructive"
		>
			{t('Stop')}
		</Button>
	{/snippet}
</ChatMessageActionCard>
