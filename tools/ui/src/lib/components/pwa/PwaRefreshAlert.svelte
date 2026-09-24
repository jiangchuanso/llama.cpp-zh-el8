<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	import { t } from '$lib/i18n';

	let { forceReload, needRefresh: needRefreshProp, updateServiceWorker } = $props();
	let needRefresh = $derived(needRefreshProp ?? false);
</script>

{#if needRefresh}
	<Card.Root class="overflow-hidden gap-1 py-5">
		<Card.Header class="px-5">
			<Card.Title class="text-sm font-medium">{t('Update available')}</Card.Title>
		</Card.Header>

		<Card.Content class="gap-6 grid px-5">
			<p class="text-xs text-muted-foreground">
				{t('A new version is available. Reload to update.')}
			</p>

			<Button
				class="justify-self-end-safe"
				onclick={() => {
					updateServiceWorker();

					if (forceReload) {
						window.location.reload();
					}

					needRefresh = false;
				}}
				size="sm"
			>
				{t('Reload')}
			</Button>
		</Card.Content>
	</Card.Root>
{/if}
