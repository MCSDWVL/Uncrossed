export const EPOCH = '2000-01-01';
export const COOLDOWN_DAYS = 90;
export function validSeed(value) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value || '')) return false;
  const date = new Date(`${value}T12:00:00Z`);
  return !Number.isNaN(date.valueOf()) && date.toISOString().slice(0, 10) === value;
}
export function usableSeed(value) { return typeof value === 'string' && value.length > 0 && value.length <= 128; }
function hash(text) { let h = 2166136261; for (const char of text) h = Math.imul(h ^ char.charCodeAt(0), 16777619); return h >>> 0; }
function rngFor(seed) { let state = hash(seed); return () => { state |= 0; state = state + 0x6D2B79F5 | 0; let t = Math.imul(state ^ state >>> 15, 1 | state); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function dayDistance(seed) { return Math.round((Date.parse(`${seed}T12:00:00Z`) - Date.parse(`${EPOCH}T12:00:00Z`)) / 86400000); }
export function supported(answer, clues) { const counts = {}; for (const char of answer.word.toUpperCase()) counts[char] = (counts[char] || 0) + 1; return Object.entries(counts).every(([letter, count]) => ((Array.isArray(clues[letter]) ? clues[letter].length : clues[letter]) || 0) >= count); }
export function scheduledAnswer(seed, answers, clues) {
  const pool = answers.filter((answer) => supported(answer, clues));
  if (pool.length <= COOLDOWN_DAYS) throw new Error(`Need more than ${COOLDOWN_DAYS} supported answers for cooldown.`);
  // A stable shuffled cycle gives a 90-day no-repeat guarantee without
  // replaying every earlier calendar day at startup.
  const ordered = [...pool].sort((left, right) => {
    const delta = hash(`answer:${left.word}`) - hash(`answer:${right.word}`);
    return delta || left.word.localeCompare(right.word);
  });
  const position = validSeed(seed) ? Math.max(0, dayDistance(seed)) : hash(`seed:${seed}`);
  return ordered[position % ordered.length];
}
export function assignClues(answer, seed, clues) {
  const random = rngFor(`clues:${seed}`), used = new Set();
  return [...answer.word.toUpperCase()].map((letter) => {
    const choices = clues[letter].filter((clue) => !used.has(clue.id));
    // Reserve one in five E puzzles for footwear-width clues. The category is
    // selected by seed, so a shared puzzle always presents the same clue.
    const wantsShoeSize = letter === 'E' && hash(`shoe-size:${seed}:E`) % 5 === 0;
    const preferred = choices.filter((clue) => wantsShoeSize ? clue.topic === 'shoe-size' : clue.topic !== 'shoe-size');
    const pool = preferred.length ? preferred : choices;
    const clue = pool[Math.floor(random() * pool.length)]; used.add(clue.id); return clue;
  });
}
