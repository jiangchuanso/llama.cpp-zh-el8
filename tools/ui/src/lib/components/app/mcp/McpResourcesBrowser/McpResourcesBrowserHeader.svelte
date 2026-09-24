<script lang="ts">
	import { Loader2, RefreshCw } from '@lucide/svelte';
	import { SearchInput } from '$lib/components/app/forms';
	import { Button } from '$lib/components/ui/button';
	import { ICON_CLASS_DEFAULT } from '$lib/constants';
	import { t } from '$lib/i18n';

	interface Props {
		isLoading: boolean;
		onRefresh: () => void;
		onSearch?: (query: string) => void;
		searchQuery?: string;
	}

	let { isLoading, onRefresh, onSearch, searchQuery = '' }: Props = $props();
</script>

<div class="flex flex-col gap-2">
	<div class="mb-2 flex items-center gap-4">
		<SearchInput
			onInput={(value) => onSearch?.(value)}
			placeholder="Search resources..."
			value={searchQuery}
		/>

		<Button
			class="h-8 w-8 p-0"
			disabled={isLoading}
			onclick={onRefresh}
			size="sm"
			title={t('Refresh resources')}
			variant="ghost"
		>
			{#if isLoading}
				<Loader2 class="{ICON_CLASS_DEFAULT} animate-spin" />
			{:else}
				<RefreshCw class={ICON_CLASS_DEFAULT} />
			{/if}
		</Button>
	</div>

	<h3 class="text-sm font-medium">{t('Available resources')}</h3>
</div>
