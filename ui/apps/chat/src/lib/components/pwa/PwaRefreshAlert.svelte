<script lang="ts">
	import { Button } from '@ggml-org/llama-ui/ui/button';
	import { t } from '#lib/i18n/index.ts';
	import * as Card from '@ggml-org/llama-ui/ui/card';

	let { needRefresh: needRefreshProp, updateServiceWorker } = $props();
	let needRefresh = $derived(needRefreshProp ?? false);
</script>

{#if needRefresh}
	<Card.Root class="overflow-hidden gap-1 py-5">
		<Card.Header class="px-5">
			<Card.Title class="text-body-sm font-medium">{t('Update available')}</Card.Title>
		</Card.Header>

		<Card.Content class="gap-6 grid px-5">
			<p class="text-caption text-muted-foreground">
				{t('A new version is available. Reload to update.')}
			</p>

			<Button
				class="justify-self-end-safe"
				onclick={() => {
					void updateServiceWorker();
					needRefresh = false;
				}}
				size="sm"
			>
				{t('Reload')}
			</Button>
		</Card.Content>
	</Card.Root>
{/if}
