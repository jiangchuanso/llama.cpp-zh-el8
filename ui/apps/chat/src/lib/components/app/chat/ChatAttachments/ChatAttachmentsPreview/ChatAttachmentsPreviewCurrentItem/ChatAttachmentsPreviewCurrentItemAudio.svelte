<script lang="ts">
	import { VoiceTranscriptStatus } from '@ggml-org/llama-ui/voice';
	import { Music } from '@lucide/svelte';
	import { VOICE_MESSAGE_LABEL } from '#lib/constants/index.ts';
	import { voiceTranscriptsStore } from '#lib/stores/index.ts';
	import type { ChatAttachmentDisplayItem } from '#lib/types/index.ts';
	import { voiceAttachmentSource } from '#lib/utils/voice-attachment.ts';
	import { t } from '#lib/i18n/index.ts';

	interface Props {
		currentItem: ChatAttachmentDisplayItem | null;
		audioSrc: string | null;
	}

	let { audioSrc, currentItem }: Props = $props();

	let source = $derived(currentItem ? voiceAttachmentSource(currentItem) : null);
	// a voice message's transcript, from the message or still on its way
	let shown = $derived(source ? voiceTranscriptsStore.shown(source.name, source.transcript) : null);
	let transcript = $derived(shown?.transcript);
	let transcribing = $derived(shown?.status === VoiceTranscriptStatus.TRANSCRIBING);
</script>

<div class="flex flex-1 items-center justify-center p-8">
	<div class="w-full max-w-md text-center">
		<Music class="mx-auto mb-4 size-16 text-white/50" />

		{#if audioSrc}
			<audio class="mb-4 w-full" controls src={audioSrc}>
				{t('Your browser does not support the audio element.')}
			</audio>
		{:else}
			<p class="mb-4 text-white/70">{t('Audio preview not available')}</p>
		{/if}

		<p class="text-body-sm text-white/50">
			{source?.voice ? t(VOICE_MESSAGE_LABEL) : currentItem?.name || t('Audio')}
		</p>

		{#if transcript}
			<p
				class="mt-6 max-h-[40vh] overflow-y-auto text-left text-body-sm whitespace-pre-wrap text-white/80"
				data-slot="voice-preview-transcript"
			>
				<span class="sr-only">{t('Transcript: ')}</span>{transcript}
			</p>
		{:else if transcribing}
			<p class="mt-6 text-caption text-white/50">{t('Transcribing...')}</p>
		{/if}
	</div>
</div>
