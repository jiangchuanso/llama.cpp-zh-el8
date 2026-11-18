<script lang="ts">
	import { Button } from '@ggml-org/llama-ui/ui/button';
	import { Pencil, RefreshCw, Trash2 } from '@lucide/svelte';
	import { t } from '#lib/i18n/index.ts';

	interface Props {
		isHealthChecking: boolean;
		onEdit: () => void;
		onRefresh: () => void;
		onDelete: () => void;
	}

	let { isHealthChecking, onDelete, onEdit, onRefresh }: Props = $props();
</script>

<div class="flex shrink-0 items-center gap-1">
	<Button aria-label={t('Edit')} class="size-7" onclick={onEdit} size="icon" variant="ghost">
		<Pencil class="size-icon-md" />
	</Button>

	<Button
		aria-label={t('Refresh')}
		class="size-7"
		disabled={isHealthChecking}
		onclick={onRefresh}
		size="icon"
		variant="ghost"
	>
		<RefreshCw class="size-icon-md" />
	</Button>

	<Button
		aria-label={t('Delete')}
		class="hover:text-destructive-foreground size-7 text-destructive hover:bg-destructive/10"
		onclick={onDelete}
		size="icon"
		variant="ghost"
	>
		<Trash2 class="size-icon-md" />
	</Button>
</div>
