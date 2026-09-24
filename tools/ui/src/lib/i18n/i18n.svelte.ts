/**
 * Minimal, dependency-free i18n for llama-ui.
 *
 * The English source text is used as the translation key. Any string without a
 * translation falls back to the source, so:
 *   - the UI never renders an empty/missing value, and
 *   - new upstream strings keep working until a translation is added.
 *
 * Only the current locale lives here; the user's choice is persisted with the
 * rest of the settings (see settingsStore), which is why `initI18n` is called
 * from there. This keeps a single source of truth for the preference.
 */

import { ZH_CN } from './locales/zh-CN';
import { browser } from '$app/environment';

export type Locale = 'en' | 'zh-CN';
/** User preference: an explicit locale, or 'auto' to follow the browser. */
export type LocalePreference = 'auto' | Locale;

export const LOCALES: ReadonlyArray<{ label: string; value: Locale }> = [
	{ label: 'English', value: 'en' },
	{ label: '简体中文', value: 'zh-CN' }
];

/** Options for the Language selector in Settings. */
export const LOCALE_PREFERENCE_OPTIONS: ReadonlyArray<{ label: string; value: LocalePreference }> =
	[{ label: 'Auto', value: 'auto' }, ...LOCALES];

const DICTIONARIES: Record<Locale, Record<string, string>> = {
	en: {},
	'zh-CN': ZH_CN
};

function isLocale(value: unknown): value is Locale {
	return value === 'en' || value === 'zh-CN';
}

export function normalizePreference(value: unknown): LocalePreference {
	return value === 'auto' || isLocale(value) ? value : 'auto';
}

function detectLocale(): Locale {
	if (!browser) return 'en';

	return navigator.language?.toLowerCase().startsWith('zh') ? 'zh-CN' : 'en';
}

let preference = $state<LocalePreference>('auto');

function resolveLocale(value: LocalePreference): Locale {
	return isLocale(value) ? value : detectLocale();
}

function applyDocumentLang(value: Locale): void {
	if (browser) document.documentElement.lang = value;
}

/** Current UI locale, resolved from the preference ('auto' = browser language). */
export function getLocale(): Locale {
	return resolveLocale(preference);
}

export function getLocalePreference(): LocalePreference {
	return preference;
}

/**
 * Update the locale preference. Called by settingsStore on startup and import,
 * and by the Language selector for instant feedback before "Save settings".
 */
export function initI18n(value: unknown): void {
	preference = normalizePreference(value);
	applyDocumentLang(getLocale());
}

/**
 * Translate an English source string.
 *
 * @param source English text used as the lookup key (also the fallback).
 * @param params Optional `{placeholder}` values to interpolate. When omitted,
 *   the string is returned verbatim so literal braces (e.g. `{{USER}}`) survive.
 */
export function t(source: string, params?: Record<string, string | number>): string {
	const translated = DICTIONARIES[getLocale()]?.[source] ?? source;

	return params ? interpolate(translated, params) : translated;
}

function interpolate(template: string, params: Record<string, string | number>): string {
	return template.replace(/\{(\w+)\}/g, (match, key: string) =>
		key in params ? String(params[key]) : match
	);
}
