<script lang="ts">
	import SettingsChatImportExportSection from './SettingsChatImportExportSection.svelte';
	import { Download, Trash2, Upload } from '@lucide/svelte';
	import {
		DialogConfirmation,
		DialogConversationSelection,
		DialogExportSettings
	} from '$lib/components/app';
	import SettingsGroup from '$lib/components/app/settings/SettingsGroup.svelte';
	import { ConversationSelectionMode, FileExtensionText, HtmlInputType } from '$lib/enums';
	import { t } from '$lib/i18n';
	import { ConversationTransferService } from '$lib/services';
	import { conversationsStore, settingsStore } from '$lib/stores';
	import { createMessageCountMap } from '$lib/utils';
	import { fade } from 'svelte/transition';
	import { toast } from 'svelte-sonner';

	let exportedConversations = $state<DatabaseConversation[]>([]);
	let importedConversations = $state<DatabaseConversation[]>([]);
	let showExportSummary = $state(false);
	let showImportSummary = $state(false);

	let showExportDialog = $state(false);
	let showImportDialog = $state(false);
	let availableConversations = $state<DatabaseConversation[]>([]);
	let messageCountMap = $state<Map<string, number>>(new Map());
	let fullImportData = $state<Array<{ conv: DatabaseConversation; messages: DatabaseMessage[] }>>(
		[]
	);

	// Delete functionality state
	let showDeleteDialog = $state(false);

	// Settings import/export state
	let showSettingsExportSummary = $state(false);
	let showSettingsImportSummary = $state(false);
	let showSettingsExportDialog = $state(false);
	let includeSensitiveData = $state(false);

	function handleSettingsExport() {
		showSettingsExportDialog = true;
		includeSensitiveData = false;
	}

	function handleSettingsExportConfirm() {
		showSettingsExportDialog = false;

		try {
			const data = settingsStore.exportSettings(includeSensitiveData);
			const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
			const url = URL.createObjectURL(blob);
			const a = document.createElement('a');

			a.href = url;
			a.download = `llama_settings_${new Date().toISOString().split('T')[0]}.json`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			URL.revokeObjectURL(url);

			showSettingsExportSummary = true;
			showSettingsImportSummary = false;
			toast.success(t('Settings exported'));
		} catch (err) {
			console.error('Failed to export settings:', err);
			toast.error(t('Failed to export settings'));
		}
	}

	function handleSettingsExportCancel() {
		showSettingsExportDialog = false;
	}

	function handleSettingsImport() {
		try {
			const input = document.createElement('input');

			input.type = HtmlInputType.FILE;
			input.accept = FileExtensionText.JSON;

			input.onchange = async (e) => {
				const file = (e.target as HTMLInputElement)?.files?.[0];

				if (!file) return;

				try {
					const text = await file.text();
					const data = JSON.parse(text);

					if (!data || typeof data !== 'object' || !data.config) {
						toast.error(t('Invalid settings file: missing config'));

						return;
					}

					settingsStore.importSettings(data);

					showSettingsImportSummary = true;
					showSettingsExportSummary = false;
					toast.success(t('Settings imported successfully'));
				} catch (err) {
					console.error('Failed to import settings:', err);
					toast.error(t('Failed to import settings'));
				}
			};

			input.click();
		} catch (err) {
			console.error('Failed to open file picker:', err);
			toast.error(t('Failed to open file picker'));
		}
	}

	async function handleExportClick() {
		try {
			const allConversations = conversationsStore.conversations;

			if (allConversations.length === 0) {
				toast.info(t('No conversations to export'));

				return;
			}

			const conversationsWithMessages = await Promise.all(
				allConversations.map(async (conv: DatabaseConversation) => {
					const messages = await conversationsStore.getConversationMessages(conv.id);

					return { conv, messages };
				})
			);

			messageCountMap = createMessageCountMap(conversationsWithMessages);
			availableConversations = allConversations;
			showExportDialog = true;
		} catch (err) {
			console.error('Failed to load conversations:', err);
			alert(t('Failed to load conversations'));
		}
	}

	async function handleExportConfirm(selectedConversations: DatabaseConversation[]) {
		try {
			const allData = await conversationsStore.getConversationsForExport(
				selectedConversations.map((conv) => conv.id)
			);

			if (allData.length === 1) {
				ConversationTransferService.downloadConversationFile(allData[0]);
			} else {
				ConversationTransferService.downloadConversationsArchive(allData);
			}

			exportedConversations = selectedConversations;
			showExportSummary = true;
			showImportSummary = false;
			showExportDialog = false;
		} catch (err) {
			console.error('Export failed:', err);
			alert(t('Failed to export conversations'));
		}
	}

	async function handleImportClick() {
		try {
			const input = document.createElement('input');

			// No `accept` filter: iOS resolves each entry to a UTI and has none for
			// `.jsonl`, which greys out exported conversations in the file picker.
			// `parseImportFile` detects the format from the file contents instead.
			input.type = HtmlInputType.FILE;

			input.onchange = async (e) => {
				const file = (e.target as HTMLInputElement)?.files?.[0];

				if (!file) return;

				try {
					const importedData = await ConversationTransferService.parseImportFile(file);

					if (importedData.length === 0) {
						throw new Error('No conversations found in file');
					}

					fullImportData = importedData;
					availableConversations = importedData.map((item) => item.conv);
					messageCountMap = createMessageCountMap(importedData);
					showImportDialog = true;
				} catch (err: unknown) {
					const message = err instanceof Error ? err.message : 'Unknown error';

					console.error('Failed to parse file:', err);
					alert(t('Failed to parse file: {message}', { message }));
				}
			};

			input.click();
		} catch (err) {
			console.error('Import failed:', err);
			alert(t('Failed to import conversations'));
		}
	}

	async function handleImportConfirm(selectedConversations: DatabaseConversation[]) {
		try {
			const selectedIds = new Set(selectedConversations.map((c) => c.id));
			const selectedData = $state
				.snapshot(fullImportData)
				.filter((item) => selectedIds.has(item.conv.id));
			const { imported, skipped } = await conversationsStore.importConversationsData(selectedData);

			// A conversation already in the database is left untouched, so the summary
			// lists what was written and the toast accounts for the rest.
			if (skipped.length > 0) {
				toast.info(
					t('Skipped {count} conversations already in your library', {
						count: skipped.length
					})
				);
			}

			importedConversations = imported;
			showImportSummary = true;
			showExportSummary = false;
			showImportDialog = false;
		} catch (err) {
			console.error('Import failed:', err);
			alert(t('Failed to import conversations. Please check the file format.'));
		}
	}

	async function handleDeleteAllClick() {
		try {
			const allConversations = conversationsStore.conversations;

			if (allConversations.length === 0) {
				toast.info(t('No conversations to delete'));

				return;
			}

			showDeleteDialog = true;
		} catch (err) {
			console.error('Failed to load conversations for deletion:', err);
			toast.error(t('Failed to load conversations'));
		}
	}

	async function handleDeleteAllConfirm() {
		try {
			await conversationsStore.deleteAll();

			showDeleteDialog = false;
		} catch (err) {
			console.error('Failed to delete conversations:', err);
		}
	}

	function handleDeleteAllCancel() {
		showDeleteDialog = false;
	}
</script>

<div in:fade={{ duration: 150 }} class="space-y-12">
	<SettingsGroup title={t('Conversations')}>
		<SettingsChatImportExportSection
			IconComponent={Download}
			buttonText={t('Export conversations')}
			description={t(
				'Download your conversations as a ZIP of JSONL files. This includes all messages, attachments, and conversation history.'
			)}
			onclick={handleExportClick}
			summary={{ items: exportedConversations, show: showExportSummary, verb: t('Exported') }}
			title={t('Export')}
		/>

		<SettingsChatImportExportSection
			IconComponent={Upload}
			buttonText={t('Import conversations')}
			description={t(
				'Import one or more conversations from a previously exported ZIP or JSONL file. This will merge with your existing conversations.'
			)}
			onclick={handleImportClick}
			summary={{ items: importedConversations, show: showImportSummary, verb: t('Imported') }}
			title={t('Import')}
		/>

		<SettingsChatImportExportSection
			IconComponent={Trash2}
			buttonClass="text-destructive-foreground justify-start justify-self-start bg-destructive hover:bg-destructive/80 md:w-auto"
			buttonText={t('Delete all conversations')}
			buttonVariant="destructive"
			description={t(
				'Permanently delete all conversations and their messages. This action cannot be undone. Consider exporting your conversations first if you want to keep a backup.'
			)}
			onclick={handleDeleteAllClick}
			title={t('Delete All')}
			titleClass="text-destructive"
		/>
	</SettingsGroup>

	<SettingsGroup title={t('Settings')}>
		<SettingsChatImportExportSection
			IconComponent={Download}
			buttonText={t('Export settings')}
			description={t('Export your chat settings and preferences as a JSON file.')}
			onclick={handleSettingsExport}
			summary={{ items: [], show: showSettingsExportSummary, verb: t('Exported') }}
			title={t('Export')}
		/>

		<SettingsChatImportExportSection
			IconComponent={Upload}
			buttonText={t('Import settings')}
			description={t(
				'Import chat settings from a previously exported JSON file. This will merge with your existing settings.'
			)}
			onclick={handleSettingsImport}
			summary={{ items: [], show: showSettingsImportSummary, verb: t('Imported') }}
			title={t('Import')}
		/>
	</SettingsGroup>
</div>

<DialogExportSettings
	bind:includeSensitiveData
	bind:open={showSettingsExportDialog}
	onCancel={handleSettingsExportCancel}
	onConfirm={handleSettingsExportConfirm}
/>

<DialogConversationSelection
	bind:open={showExportDialog}
	conversations={availableConversations}
	{messageCountMap}
	mode={ConversationSelectionMode.EXPORT}
	onCancel={() => (showExportDialog = false)}
	onConfirm={handleExportConfirm}
/>

<DialogConversationSelection
	bind:open={showImportDialog}
	conversations={availableConversations}
	{messageCountMap}
	mode={ConversationSelectionMode.IMPORT}
	onCancel={() => (showImportDialog = false)}
	onConfirm={handleImportConfirm}
/>

<DialogConfirmation
	bind:open={showDeleteDialog}
	cancelText={t('Cancel')}
	confirmText={t('Delete All')}
	description={t(
		'Are you sure you want to delete all conversations? This action cannot be undone and will permanently remove all your conversations and messages.'
	)}
	icon={Trash2}
	onCancel={handleDeleteAllCancel}
	onConfirm={handleDeleteAllConfirm}
	title={t('Delete all conversations')}
	variant="destructive"
/>
