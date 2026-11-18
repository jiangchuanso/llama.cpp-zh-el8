<script lang="ts">
	import * as AlertDialog from '@ggml-org/llama-ui/ui/alert-dialog';
	import { t } from '#lib/i18n/index.ts';

	interface Props {
		open: boolean;
		displayName: string;
		onOpenChange: (open: boolean) => void;
		onConfirm: () => void;
	}

	let { displayName, onConfirm, onOpenChange, open = $bindable() }: Props = $props();
</script>

<AlertDialog.Root bind:open {onOpenChange}>
	<AlertDialog.Content>
		<AlertDialog.Header>
			<AlertDialog.Title>{t('Delete Server')}</AlertDialog.Title>

			<AlertDialog.Description>
				{t('Are you sure you want to delete')} <strong>{displayName}</strong>{t(
					'? This action cannot be undone.'
				)}
			</AlertDialog.Description>
		</AlertDialog.Header>

		<AlertDialog.Footer>
			<AlertDialog.Cancel>{t('Cancel')}</AlertDialog.Cancel>

			<AlertDialog.Action onclick={onConfirm} variant="destructive">Delete</AlertDialog.Action>
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>
