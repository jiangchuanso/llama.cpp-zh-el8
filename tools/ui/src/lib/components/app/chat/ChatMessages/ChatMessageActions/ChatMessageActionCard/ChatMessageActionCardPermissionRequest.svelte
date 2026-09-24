<script lang="ts">
	import { ChevronDown, ShieldQuestion } from '@lucide/svelte';
	import { ChatMessageActionCard } from '$lib/components/app';
	import { Button, buttonVariants } from '$lib/components/ui/button';
	import * as ButtonGroup from '$lib/components/ui/button-group';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu';
	import { cn } from '$lib/components/ui/utils';
	import { TOOL_SERVER_LABELS } from '$lib/constants';
	import { ToolPermissionDecision, ToolSource } from '$lib/enums';
	import { t } from '$lib/i18n';
	import { toolsStore } from '$lib/stores';

	interface Props {
		toolName: string;
		serverLabel: string;
		onDecision: (decision: ToolPermissionDecision) => void;
	}

	let { onDecision, serverLabel, toolName }: Props = $props();
</script>

<ChatMessageActionCard icon={ShieldQuestion}>
	{#snippet message()}
		{#if serverLabel}
			{t('Allow use of {tool} from {server}?', { server: serverLabel, tool: toolName })}
		{:else}
			{t('Allow use of {tool}?', { tool: toolName })}
		{/if}
	{/snippet}

	{#snippet actions()}
		<DropdownMenu.Root>
			<ButtonGroup.Root class="overflow-hidden rounded-md shadow-sm">
				<Button
					class="!rounded-r-none !shadow-none"
					onclick={() => onDecision(ToolPermissionDecision.ONCE)}
					size="sm"
					variant="secondary"
				>
					{t('Allow once')}
				</Button>

				<ButtonGroup.Separator />

				<DropdownMenu.Trigger
					aria-label={t('More allow options')}
					class={cn(
						buttonVariants({ size: 'sm', variant: 'secondary' }),
						'inline-flex cursor-pointer items-center !rounded-l-none !shadow-none !px-2'
					)}
				>
					<ChevronDown class="h-3.5 w-3.5" />
				</DropdownMenu.Trigger>
			</ButtonGroup.Root>

			<DropdownMenu.Content align="start" class="min-w-[8rem]">
				<DropdownMenu.Item onclick={() => onDecision(ToolPermissionDecision.ALWAYS)}>
					{t('Always allow')} <pre>{toolName}</pre>
					{t('tool')}
				</DropdownMenu.Item>

				{#if serverLabel}
					<DropdownMenu.Item onclick={() => onDecision(ToolPermissionDecision.ALWAYS_SERVER)}>
						{t('Always allow all tools from {server}', { server: serverLabel })}
					</DropdownMenu.Item>
				{:else}
					{@const source = toolsStore.getToolSource(toolName)}
					{@const providerName = t(
						source === ToolSource.SERVER
							? TOOL_SERVER_LABELS[ToolSource.SERVER]
							: source === ToolSource.CUSTOM
								? TOOL_SERVER_LABELS[ToolSource.CUSTOM]
								: 'MCP Tools'
					)}
					<DropdownMenu.Item onclick={() => onDecision(ToolPermissionDecision.ALWAYS_SERVER)}>
						{t('Approve all tools from {provider}', { provider: providerName })}
					</DropdownMenu.Item>
				{/if}
			</DropdownMenu.Content>
		</DropdownMenu.Root>

		<Button onclick={() => onDecision(ToolPermissionDecision.DENY)} size="sm" variant="destructive">
			{t('Deny')}
		</Button>
	{/snippet}
</ChatMessageActionCard>
