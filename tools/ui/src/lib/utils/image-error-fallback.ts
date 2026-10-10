import { t } from '$lib/i18n';

/**
 * Simplified HTML fallback for external images that fail to load.
 * Displays a centered message with a link to open the image in a new tab.
 */
export function getImageErrorFallbackHtml(src: string): string {
	return `<div class="image-error-content">
		<span>${t('Image cannot be displayed')}</span>
		<a href="${src}" target="_blank" rel="noopener noreferrer">${t('(open link)')}</a>
	</div>`;
}
