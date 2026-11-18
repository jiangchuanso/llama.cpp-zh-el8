import fs from 'node:fs';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const repo = 'e:/llama.cpp-el8';
const git = (a) => execFileSync('git', a, { cwd: repo, encoding: 'utf-8', maxBuffer: 64 * 1024 * 1024 });
git(['add', '-A']);

function walk(dir, acc = []) {
	for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
		const p = path.join(dir, e.name);
		if (e.isDirectory()) walk(p, acc);
		else if (/\.(svelte|ts)$/.test(e.name)) acc.push(p);
	}
	return acc;
}
const files = ['ui/apps/chat/src', 'ui/lib/ui/src'].flatMap(r => walk(path.join(repo, r)));
const dict = fs.readFileSync(`${repo}/ui/apps/chat/src/lib/i18n/locales/zh-CN.ts`, 'utf-8');
function keyExists(k) {
	return dict.includes(`'${k}':`) || dict.includes(`"${k}":`) ||
		(/^[A-Za-z_]\w*$/.test(k) && new RegExp(`^[ \\t]*${k}[ \\t]*:[ \\t]*['\"]`, 'm').test(dict));
}
const missingImport = [], missingKeys = new Set();
let tFiles = 0, tCalls = 0;
for (const f of files) {
	const s = fs.readFileSync(f, 'utf-8');
	const calls = [...s.matchAll(/\bt\(\s*'((?:[^'\\]|\\.)*)'/g)];
	if (!calls.length) continue;
	tFiles++; tCalls += calls.length;
	if (!/\bimport\s*\{[^}]*\bt\b[^}]*\}\s*from/.test(s)) missingImport.push(path.relative(repo, f));
	for (const m of calls) {
		const k = m[1].replace(/\\'/g, "'");
		if (!keyExists(k)) missingKeys.add(k);
	}
}
console.log(`tFiles=${tFiles} tCalls=${tCalls} missingImport=${missingImport.length} missingKeys=${missingKeys.size}`);
for (const f of missingImport) console.log(`  NOIMPORT: ${f}`);
for (const k of missingKeys) console.log(`  NOKEY: ${k}`);
const unmerged = git(['diff', '--name-only', '--diff-filter=U']).trim();
console.log(`unmerged=${unmerged ? unmerged.split(/\r?\n/).length : 0}`);
const staged = git(['diff', '--cached', '--name-only']);
console.log(`staged-files=${staged.split(/\r?\n/).filter(Boolean).length}`);
fs.rmSync(path.join(repo, '_final_check.mjs'), { force: true });
