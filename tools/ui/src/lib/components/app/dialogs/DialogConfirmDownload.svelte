<script lang="ts">
	import DialogConfirmation from '$lib/components/app/dialogs/DialogConfirmation.svelte';
	import { ModelDownloadConfirmAction } from '$lib/enums';
	import { t } from '$lib/i18n';
	import { modelsStore } from '$lib/stores';

	interface Props {
		/** Action being confirmed; drives the wording. */
		action: ModelDownloadConfirmAction;
		/** `<repo>:<tag>` the action targets. */
		repoWithTag: string;
		onClose: () => void;
		/** Overrides the default store removal; defaults to removing the entry. */
		onConfirm?: (repoWithTag: string) => void;
		open?: boolean;
	}

	let { action, onClose, onConfirm, open = true, repoWithTag }: Props = $props();

	// Both actions resolve through the same store removal (cancelDownload drops a
	// running download's partial files or a cached model's files); only the copy
	// differs. One component so the discover chips and the selector rows word the
	// destructive confirmations identically.
	const COPY = {
		[ModelDownloadConfirmAction.CANCEL]: {
			cancelText: t('Keep downloading'),
			confirmText: t('Cancel download'),
			description: (name: string) =>
				t('This stops the download of {name} and removes the partial files. Pause it instead to keep the progress.', {
					name
				}),
			title: t('Cancel download')
		},
		[ModelDownloadConfirmAction.DELETE]: {
			cancelText: t('Keep model'),
			confirmText: t('Delete'),
			description: (name: string) =>
				t('This permanently removes {name} from disk. You can download it again later.', { name }),
			title: t('Delete model')
		}
	} as const;

	let copy = $derived(COPY[action]);
	let displayName = $derived(modelsStore.toDisplayName(repoWithTag));

	function confirm() {
		if (onConfirm) onConfirm(repoWithTag);
		else void modelsStore.status.cancelDownload(repoWithTag);

		onClose();
	}
</script>

<DialogConfirmation
	cancelText={copy.cancelText}
	confirmText={copy.confirmText}
	description={copy.description(displayName)}
	onCancel={onClose}
	onConfirm={confirm}
	{open}
	title={copy.title}
	variant="destructive"
/>
