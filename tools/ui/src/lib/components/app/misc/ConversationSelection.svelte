<script lang="ts">
	import SearchInput from '$lib/components/app/forms/SearchInput.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Checkbox } from '$lib/components/ui/checkbox';
	import { ScrollArea } from '$lib/components/ui/scroll-area';
	import { UI_DATA_ATTRS } from '$lib/constants';
	import { useMarqueeSelection } from '$lib/hooks/use-marquee-selection.svelte';
	import { t } from '$lib/i18n';
	import { SvelteSet } from 'svelte/reactivity';

	interface Props {
		conversations: DatabaseConversation[];
		messageCountMap?: Map<string, number>;
		mode: 'export' | 'import';
		onCancel: () => void;
		onConfirm: (selectedConversations: DatabaseConversation[]) => void;
		isOpen?: boolean;
	}

	let {
		conversations,
		isOpen = true,
		messageCountMap = new Map(),
		mode,
		onCancel,
		onConfirm
	}: Props = $props();

	let searchQuery = $state('');
	let selectedIds = $state.raw<SvelteSet<string>>(getInitialSelectedIds());

	function getInitialSelectedIds(): SvelteSet<string> {
		return new SvelteSet(conversations.map((c) => c.id));
	}

	let filteredConversations = $derived(
		conversations.filter((conv) => {
			const name = conv.name || t('Untitled conversation');

			return name.toLowerCase().includes(searchQuery.toLowerCase());
		})
	);

	let orderedIds = $derived(filteredConversations.map((c) => c.id));

	let allSelected = $derived(
		filteredConversations.length > 0 &&
			filteredConversations.every((conv) => selectedIds.has(conv.id))
	);

	let someSelected = $derived(
		filteredConversations.some((conv) => selectedIds.has(conv.id)) && !allSelected
	);

	const marquee = useMarqueeSelection({
		enabled: () => isOpen,
		orderedIds: () => orderedIds,
		selectedIds: () => selectedIds
	});

	function toggleAll() {
		const newSet = new SvelteSet(selectedIds);

		if (allSelected) {
			filteredConversations.forEach((conv) => newSet.delete(conv.id));
		} else {
			filteredConversations.forEach((conv) => newSet.add(conv.id));
		}

		selectedIds = newSet;
	}

	function handleConfirm() {
		const selected = conversations.filter((conv) => selectedIds.has(conv.id));

		onConfirm(selected);
	}

	function handleCancel() {
		selectedIds = getInitialSelectedIds();
		searchQuery = '';
		marquee.reset();

		onCancel();
	}

	export function reset() {
		selectedIds = getInitialSelectedIds();
		searchQuery = '';
		marquee.reset();
	}
</script>

<div class="space-y-4">
	<SearchInput bind:value={searchQuery} placeholder="Search conversations..." />

	<div class="flex items-center justify-between text-sm text-muted-foreground">
		<span>
			{t('{selected} of {total} selected', {
				selected: selectedIds.size,
				total: conversations.length
			})}
			{#if searchQuery}
				{t('({count} shown)', { count: filteredConversations.length })}
			{/if}
		</span>
	</div>

	<div class="overflow-hidden rounded-md border">
		<ScrollArea class="h-100">
			<table class="w-full">
				<thead class="sticky top-0 z-10 bg-muted">
					<tr class="border-b">
						<th class="w-12 p-3 text-left">
							<Checkbox
								checked={allSelected}
								indeterminate={someSelected}
								onCheckedChange={toggleAll}
							/>
						</th>

						<th class="p-3 text-left text-sm font-medium">{t('Conversation Name')}</th>

						<th class="w-32 p-3 text-left text-sm font-medium">{t('Messages')}</th>
					</tr>
				</thead>

				<tbody>
					{#if filteredConversations.length === 0}
						<tr>
							<td class="p-8 text-center text-sm text-muted-foreground" colspan="3">
								{#if searchQuery}
									{t('No conversations found matching "{query}"', { query: searchQuery })}
								{:else}
									{t('No conversations available')}
								{/if}
							</td>
						</tr>
					{:else}
						{#each filteredConversations as conv (conv.id)}
							{@const checked = selectedIds.has(conv.id)}
							<tr
								class="cursor-pointer border-b transition-colors hover:bg-muted/50 {checked
									? 'bg-muted/75'
									: ''}"
								{...{ [UI_DATA_ATTRS.CONVERSATION_ROW]: conv.id }}
								onclick={(event) => marquee.rowClick(conv.id, event.shiftKey)}
								onmousedown={(event) => marquee.rowMouseDown(conv.id, event)}
							>
								<td class="p-3">
									<Checkbox
										{checked}
										onclick={(event) => {
											event.preventDefault();
											event.stopPropagation();
											marquee.rowClick(conv.id, event.shiftKey);
										}}
									/>
								</td>

								<td class="p-3 text-sm">
									<div
										class="max-w-68 truncate"
										title={conv.name || t('Untitled conversation')}
									>
										{conv.name || t('Untitled conversation')}
									</div>
								</td>

								<td class="p-3 text-sm text-muted-foreground">
									{messageCountMap.get(conv.id) ?? 0}
								</td>
							</tr>
						{/each}
					{/if}
				</tbody>
			</table>
		</ScrollArea>
	</div>

	<div class="flex justify-end gap-2">
		<Button onclick={handleCancel} variant="outline">{t('Cancel')}</Button>

		<Button disabled={selectedIds.size === 0} onclick={handleConfirm}>
			{t(mode === 'export' ? 'Export' : 'Import')} ({selectedIds.size})
		</Button>
	</div>
</div>
