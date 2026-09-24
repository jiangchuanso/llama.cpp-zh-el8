<script lang="ts">
	import { Eye } from '@lucide/svelte';
	import { ActionIcon, ActionIconCopyToClipboard } from '$lib/components/app';
	import { FileTypeText } from '$lib/enums';
	import { t } from '$lib/i18n';

	interface Props {
		code: string;
		language: string;
		disabled?: boolean;
		onPreview?: (code: string, language: string) => void;
	}

	let { code, disabled = false, language, onPreview }: Props = $props();

	const showPreview = $derived(language?.toLowerCase() === FileTypeText.HTML);
</script>

<div class="code-block-actions">
	<ActionIconCopyToClipboard
		ariaLabel={disabled ? t('Code incomplete') : t('Copy code')}
		canCopy={!disabled}
		text={code}
	/>

	{#if showPreview}
		<ActionIcon
			{disabled}
			icon={Eye}
			onclick={() => onPreview!(code, language)}
			tooltip={disabled ? t('Code incomplete') : t('Preview code')}
		/>
	{/if}
</div>
