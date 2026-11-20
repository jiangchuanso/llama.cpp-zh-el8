<script lang="ts">
	import ModelsDiscoverChatTemplateDialog from './ModelsDiscoverChatTemplateDialog.svelte';
	import { t } from '#lib/i18n/index.ts';
	import ModelsDiscoverDetailsMetadataItem from './ModelsDiscoverDetailsMetadataItem.svelte';
	import { Button } from '@ggml-org/llama-ui/ui/button';
	import { MessageSquareCode } from '@lucide/svelte';
	import { modelsDiscoverStore } from '#lib/stores/index.ts';
	import type { HfModelDetailInfo, HfModelGguf } from '#lib/types/huggingface.js';
	import { formatParameters } from '#lib/utils/index.ts';

	interface Props {
		/** Full HuggingFace model id, e.g. `ggml-org/gemma-3-4b-it-GGUF`. */
		modelId: string;
		details: HfModelDetailInfo;
		gguf?: HfModelGguf;
		licenseTag: string | null;
	}

	let { details, gguf, licenseTag, modelId }: Props = $props();

	// Catalog family description when curated, else the HF card description.
	let description = $derived(
		modelsDiscoverStore.descriptionFor(modelId) ?? details.cardData?.description
	);

	let chatTemplateOpen = $state(false);
</script>

{#if description}
	<p class="text-body-sm text-muted-foreground">{description}</p>
{/if}

<!-- Metadata chips: label | value pairs, matching the HF model page style -->
<div class="flex flex-wrap items-center gap-1.5">
	{#if gguf?.total}
		<ModelsDiscoverDetailsMetadataItem
			label={t('Model size')}
			value={t('{count} params', { count: formatParameters(gguf.total) })}
		/>
	{/if}

	{#if gguf?.context_length}
		<ModelsDiscoverDetailsMetadataItem
			label={t('Context')}
			value={gguf.context_length.toLocaleString()}
		/>
	{/if}

	{#if gguf?.architecture}
		<ModelsDiscoverDetailsMetadataItem label={t('Architecture')} value={gguf.architecture} />
	{/if}

	{#if gguf?.chat_template}
		<Button
			class="h-auto gap-1.5 px-2.5 py-1 text-caption"
			onclick={() => (chatTemplateOpen = true)}
			size="sm"
			variant="secondary"
		>
			<MessageSquareCode class="size-3" />
			{t('Chat template')}
			</Button>
	{/if}

	{#if licenseTag}
		<ModelsDiscoverDetailsMetadataItem label={t('License')} value={licenseTag} />
	{/if}

	{#if details.gated === true}
		<span
			class="rounded bg-yellow-500/10 px-2 py-0.5 text-label-sm text-yellow-600 dark:text-yellow-400"
		>
			{t('gated')}
		</span>
	{/if}
</div>

{#if gguf?.chat_template}
	<ModelsDiscoverChatTemplateDialog
		bind:open={chatTemplateOpen}
		chatTemplate={gguf.chat_template}
	/>
{/if}
