<script lang="ts">
	import { t } from '$lib/i18n';

	interface Props {
		currentItem: { name?: string } | null;
		displayPreview: string | undefined;
	}

	let { currentItem, displayPreview }: Props = $props();
</script>

{#if displayPreview}
	<div class="flex flex-1 items-center justify-center">
		<img
			alt={currentItem?.name || t('preview')}
			class="max-h-[80vh] max-w-[80vw] rounded-lg object-contain shadow-lg"
			src={displayPreview}
		/>
	</div>
{/if}
