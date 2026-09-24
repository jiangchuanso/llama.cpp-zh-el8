<script lang="ts">
	import { Download, Pin, PinOff, Trash2, X } from '@lucide/svelte';
	import { ActionIcon, DialogConfirmation } from '$lib/components/app';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { TooltipSide } from '$lib/enums';
	import { t } from '$lib/i18n';

	interface Props {
		class?: string;
		selectedCount: number;
		visibleCount: number;
		allVisibleSelected: boolean;
		someVisibleSelected: boolean;
		someSelectedPinned: boolean;
		pinStateIsMixed: boolean;
		onSelectAllToggle: () => void;
		onBulkPinToggle: () => void;
		onBulkExport: () => void;
		onBulkDelete: () => void;
		onClose: () => void;
	}

	let {
		allVisibleSelected,
		class: className = '',
		onBulkDelete,
		onBulkExport,
		onBulkPinToggle,
		onClose,
		onSelectAllToggle,
		pinStateIsMixed,
		selectedCount,
		someSelectedPinned,
		someVisibleSelected,
		visibleCount
	}: Props = $props();

	let showDeleteDialog = $state(false);

	function handleDeleteClick() {
		showDeleteDialog = true;
	}

	function handleDeleteConfirm() {
		showDeleteDialog = false;
		onBulkDelete();
	}

	function handleDeleteCancel() {
		showDeleteDialog = false;
	}

	const hasSelection = $derived(selectedCount > 0);
	const isMasterChecked = $derived(allVisibleSelected);
	const isMasterIndeterminate = $derived(!allVisibleSelected && someVisibleSelected);

	const pinTooltip = $derived(
		hasSelection
			? pinStateIsMixed
				? 'Unavailable for mixed state selection'
				: someSelectedPinned
					? selectedCount === 1
						? 'Unpin'
						: 'Unpin all'
					: selectedCount === 1
						? 'Pin'
						: 'Pin all'
			: 'Pin'
	);

	const pinDisabled = $derived(!hasSelection || pinStateIsMixed);
</script>

<div
	aria-label={t('Bulk actions for selected conversations')}
	class="flex items-center gap-1.5 rounded-xl border border-border/50 bg-background/50 px-2 py-1.5 shadow-sm backdrop-blur-xl {className}"
	role="toolbar"
>
	<label class="flex min-w-0 cursor-pointer items-center gap-2">
		<Checkbox
			aria-label={t(isMasterChecked ? 'Deselect all' : 'Select all')}
			checked={isMasterChecked}
			indeterminate={isMasterIndeterminate}
			onCheckedChange={onSelectAllToggle}
		/>

		<span class="truncate text-xs font-medium text-muted-foreground">
			{t('{selected} / {total} selected', { selected: selectedCount, total: visibleCount })}
		</span>
	</label>

	<div class="ml-auto flex items-center gap-0.75">
		<ActionIcon
			ariaLabel={t(pinTooltip)}
			class="h-7 w-7 rounded-md bg-transparent backdrop-blur-none hover:bg-accent! {pinDisabled
				? 'cursor-not-allowed'
				: ''} {!pinDisabled ? 'opacity-100' : 'opacity-40'}"
			disabled={pinDisabled}
			icon={someSelectedPinned ? PinOff : Pin}
			iconSize="h-3.5 w-3.5"
			onclick={onBulkPinToggle}
			size="sm"
			tooltip={t(pinTooltip)}
			tooltipSide={TooltipSide.TOP}
		/>

		<ActionIcon
			ariaLabel={t('Export selected')}
			class="h-7 w-7 rounded-md bg-transparent backdrop-blur-none hover:bg-accent! {hasSelection
				? 'opacity-100'
				: 'opacity-40'}"
			disabled={!hasSelection}
			icon={Download}
			iconSize="h-3.5 w-3.5"
			onclick={onBulkExport}
			size="sm"
			tooltip={t('Export')}
			tooltipSide={TooltipSide.TOP}
		/>

		<ActionIcon
			ariaLabel={t('Delete selected')}
			class="h-7 w-7 rounded-md bg-transparent backdrop-blur-none hover:bg-destructive/10! dark:hover:bg-destructive/20! disabled:hover:bg-transparent {hasSelection
				? 'opacity-100'
				: 'opacity-40'}"
			disabled={!hasSelection}
			icon={Trash2}
			iconSize="h-3.5 w-3.5 text-destructive"
			onclick={handleDeleteClick}
			size="sm"
			tooltip={t('Delete selected')}
			tooltipSide={TooltipSide.TOP}
		/>

		<div aria-hidden="true" class="mx-1 h-4 w-px bg-border"></div>

		<ActionIcon
			ariaLabel={t('Exit bulk selection mode')}
			class="h-7 w-7 rounded-md bg-transparent backdrop-blur-none hover:bg-accent!"
			icon={X}
			iconSize="h-3.5 w-3.5"
			onclick={onClose}
			size="sm"
			tooltip={t('Exit bulk selection mode')}
			tooltipSide={TooltipSide.TOP}
		/>
	</div>
</div>

<DialogConfirmation
	bind:open={showDeleteDialog}
	cancelText="Cancel"
	confirmText={selectedCount === 1 ? t('Delete') : t('Delete {count}', { count: selectedCount })}
	description={selectedCount === 1
		? t(
				'This action cannot be undone. The selected conversation and its messages will be permanently removed, including any forks.'
			)
		: t(
				'This action cannot be undone. The selected conversations and their messages will be permanently removed, including any forks.'
			)}
	icon={Trash2}
	onCancel={handleDeleteCancel}
	onConfirm={handleDeleteConfirm}
	title={t('Delete {count} conversations', { count: selectedCount })}
	variant="destructive"
/>
