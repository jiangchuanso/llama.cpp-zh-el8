<script lang="ts">
	import { Button, buttonVariants } from '@ggml-org/llama-ui/ui/button';
	import * as ButtonGroup from '@ggml-org/llama-ui/ui/button-group';
	import * as DropdownMenu from '@ggml-org/llama-ui/ui/dropdown-menu';
	import { cn } from '@ggml-org/llama-ui/utils';
	import { ChevronDown, ShieldQuestion } from '@lucide/svelte';
	import { ChatMessageActionCard } from '#lib/components/app/index.ts';
	import { TOOL_SERVER_LABELS } from '#lib/constants/index.ts';
	import { ToolPermissionDecision, ToolSource } from '#lib/enums/index.ts';
	import { toolsStore } from '#lib/stores/index.ts';
	import { t } from '#lib/i18n/index.ts';

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
			<ButtonGroup.Root>
				<Button onclick={() => onDecision(ToolPermissionDecision.ONCE)} size="sm" variant="outline">
					Allow once
				</Button>

				<ButtonGroup.Separator />

				<DropdownMenu.Trigger
					aria-label={t('More allow options')}
					class={cn(
						buttonVariants({ size: 'sm', variant: 'outline' }),
						'inline-flex cursor-pointer items-center !px-2'
					)}
				>
					<ChevronDown class="size-icon-sm" />
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
