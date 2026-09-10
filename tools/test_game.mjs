import { ANSWERS, CLUES } from '../js/runtime-data.js';
import { assignClues, scheduledAnswer, validSeed } from '../js/puzzle-core.js';
const assert = (condition, message) => { if (!condition) throw new Error(message); };
assert(ANSWERS.every(({ word }) => /^[a-z]+$/.test(word) && word.length >= 6 && word.length <= 10), 'Answers must be alphabetic 6–10 letter words.');
assert(Object.keys(CLUES).length === 26, 'Catalog must contain every letter.');
assert(Object.entries(CLUES).every(([letter, entries]) => entries.length >= 1 && entries.every((entry) => entry.letter === letter)), 'Starter catalog must have at least one matching clue per letter.');
assert(validSeed('2026-09-10') && !validSeed('2026-02-31'), 'Seed validation must reject invalid calendar dates.');
assert(scheduledAnswer('123aboba', ANSWERS, CLUES).word === scheduledAnswer('123aboba', ANSWERS, CLUES).word, 'An arbitrary seed must be deterministic.');
assert(scheduledAnswer('2026-09-10', ANSWERS, CLUES).word === scheduledAnswer('2026-09-10', ANSWERS, CLUES).word, 'A seed must be deterministic.');
assert(scheduledAnswer('2026-09-10', ANSWERS, CLUES).word !== scheduledAnswer('2026-09-11', ANSWERS, CLUES).word, 'Adjacent valid seeds must select different answers.');
const seen = [];
for (let day = 0; day < 730; day += 1) { const date = new Date(Date.UTC(2000, 0, 1 + day)).toISOString().slice(0, 10); const selected = scheduledAnswer(date, ANSWERS, CLUES); assert(!seen.slice(-90).includes(selected.word), `Cooldown repeated ${selected.word}`); seen.push(selected.word); const assigned = assignClues(selected, date, CLUES); assert(new Set(assigned.map((clue) => clue.id)).size === assigned.length, 'A puzzle repeated a clue.'); }
console.log('Runtime data checks passed.');
