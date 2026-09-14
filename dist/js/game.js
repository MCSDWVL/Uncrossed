import { ANSWERS as FALLBACK_ANSWERS } from './runtime-data.js';
import { assignClues, scheduledAnswer, usableSeed, validSeed } from './puzzle-core.js';

const DATA = './data';
const dataNonce = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
function stableIndex(value, length) {
  let hash = 2166136261;
  for (const character of value) hash = Math.imul(hash ^ character.charCodeAt(0), 16777619);
  return (hash >>> 0) % length;
}
async function loadJson(path) {
  // Puzzle data is intentionally always fresh; static hosting is fast enough
  // and avoids serving a previous corpus after an offline rebuild.
  const request = `${path}${path.includes('?') ? '&' : '?'}v=${dataNonce}`;
  const response = await fetch(request, { cache: 'no-store' });
  if (!response.ok) throw new Error(`${path}: ${response.status}`);
  return response.json();
}
async function loadCatalog() {
  try {
    const index = await loadJson(`${DATA}/answers-index.json`);
    if (!Array.isArray(index.answers) || !index.downCounts) throw new Error('invalid generated catalog');
    return { answers: index.answers, clueCounts: index.downCounts, generated: true };
  } catch (error) {
    console.warn('Generated catalog unavailable; using the development catalog.', error);
    const { CLUES } = await import('./generated-clues.js');
    return { answers: FALLBACK_ANSWERS, clues: CLUES, generated: false };
  }
}

const $ = (id) => document.getElementById(id);
const board = $('board');
const message = $('message');

function pacificToday() {
  const parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Los_Angeles', year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${values.year}-${values.month}-${values.day}`;
}
const querySeed = new URLSearchParams(location.search).get('seed');
const seed = usableSeed(querySeed) ? querySeed : pacificToday();
const debug = new URLSearchParams(location.search).has('debug');
let answer, clues;
const storageKey = `uncrossed:${seed}`;
let state = { letters: [], solved: false };
let activeClueIndex = null;
let acrossClueRevealed = false;

function persist() { try { localStorage.setItem(storageKey, JSON.stringify(state)); } catch { /* private browsing may deny it */ } }
function render() {
  document.body.classList.toggle('solved', state.solved);
  $('puzzle-date').textContent = validSeed(seed)
    ? new Intl.DateTimeFormat('en-US', { dateStyle: 'full', timeZone: 'America/Los_Angeles' }).format(new Date(`${seed}T12:00:00Z`))
    : `Seed: ${seed}`;
  board.replaceChildren(...clues.map((clue, index) => { const cell = document.createElement('label'); cell.className = 'cell'; cell.htmlFor = `letter-${index}`; const num = document.createElement('span'); num.className = 'cell-number'; num.textContent = index + 1; const input = document.createElement('input'); input.className = 'letter-input'; input.id = `letter-${index}`; input.maxLength = 1; input.autocomplete = 'off'; input.inputMode = 'text'; input.value = state.letters[index]; input.setAttribute('aria-label', `Letter ${index + 1}: ${clue.clue}`); input.addEventListener('focus', () => { cell.classList.add('active'); setActiveClue(index); input.select(); }); input.addEventListener('blur', () => { cell.classList.remove('active'); setActiveClue(null); }); input.addEventListener('input', () => onInput(index, input.value)); input.addEventListener('keydown', (event) => onKey(index, event)); cell.append(num, input); return cell; }));
  $('down-clues').replaceChildren(...clues.map((clue, index) => { const item = document.createElement('li'); item.classList.toggle('active', index === activeClueIndex); item.append(document.createTextNode(clue.clue)); if (clue.homophone === 'near') { const note = document.createElement('span'); note.className = 'clue-near-homophone'; note.textContent = ' (nearly a homophone)'; item.append(note); } if (debug) { const details = document.createElement('small'); details.className = 'debug-details'; details.textContent = clue.sourceAnswer ? ` [Ginsberg database answer: ${clue.sourceAnswer}; mapped to: ${answer.word[index].toUpperCase()}; ID: ${clue.id}]` : ` [${clue.mechanism}; ID: ${clue.id}]`; item.append(details); } return item; }));
  const across = document.createElement('li');
  if (acrossClueRevealed) { across.textContent = answer.hint; if (debug && answer.clueSource) { const details = document.createElement('small'); details.className = 'debug-details'; details.textContent = ` [Ginsberg database answer: ${answer.word.toUpperCase()}; ID: ${answer.clueSource.id}]`; across.append(details); } }
  else { across.className = 'spoiler'; across.setAttribute('aria-label', 'Across hint hidden'); }
  $('across-clues').replaceChildren(across);
  $('across-clues').hidden = false;
  $('across-clues').setAttribute('aria-hidden', String(!acrossClueRevealed));
  $('reveal-across').hidden = acrossClueRevealed;
  $('reveal-across').setAttribute('aria-expanded', String(acrossClueRevealed));
  if (state.solved) { message.textContent = 'Uncrossed! Come back tomorrow for another one.'; message.className = 'message good'; }
  else { message.textContent = ''; message.className = 'message'; }
}
function setActiveClue(index) {
  activeClueIndex = index;
  $('down-clues').querySelectorAll('li').forEach((item, clueIndex) => item.classList.toggle('active', clueIndex === index));
}
function focus(index) { board.querySelector(`#letter-${Math.max(0, Math.min(index, answer.word.length - 1))}`)?.focus(); }
function onInput(index, value) { const letter = value.replace(/[^a-z]/gi, '').slice(-1).toUpperCase(); state.letters[index] = letter; const input = board.querySelector(`#letter-${index}`); input.value = letter; input.closest('.cell').classList.remove('incorrect'); persist(); if (letter && index < answer.word.length - 1) focus(index + 1); check(); }
function onKey(index, event) { if (event.key === 'Backspace' && !state.letters[index] && index > 0) { event.preventDefault(); state.letters[index - 1] = ''; board.querySelector(`#letter-${index - 1}`).value = ''; persist(); focus(index - 1); } if (event.key === 'ArrowLeft') { event.preventDefault(); focus(index - 1); } if (event.key === 'ArrowRight') { event.preventDefault(); focus(index + 1); } }
function highlightIncorrect() {
  let wrong = 0;
  board.querySelectorAll('.cell').forEach((cell, index) => {
    const incorrect = Boolean(state.letters[index]) && state.letters[index] !== answer.word[index].toUpperCase();
    cell.classList.toggle('incorrect', incorrect);
    if (incorrect) wrong += 1;
  });
  return wrong;
}
function check() { if (state.letters.some((letter) => !letter) || state.solved) return; const correct = state.letters.join('') === answer.word.toUpperCase(); if (correct) { state.solved = true; message.textContent = 'Uncrossed! Come back tomorrow for another one.'; message.className = 'message good'; } else { message.textContent = 'Not quite — adjust any letters and try again.'; message.className = 'message bad'; } persist(); }
$('check-letters').addEventListener('click', () => { if (!answer || state.solved) return; const wrong = highlightIncorrect(); message.textContent = wrong ? `${wrong} incorrect letter${wrong === 1 ? '' : 's'} highlighted.` : 'No incorrect letters entered.'; message.className = wrong ? 'message bad' : 'message good'; });
$('reveal-across').addEventListener('click', () => { if (!answer) return; acrossClueRevealed = true; render(); });
$('reset').addEventListener('click', () => { if (!answer) return; state = { letters: Array(answer.word.length).fill(''), solved: false }; persist(); message.textContent = ''; message.className = 'message'; render(); focus(0); });
async function start() {
  message.textContent = 'Loading today’s puzzle…';
  try {
    const catalog = await loadCatalog();
    answer = scheduledAnswer(seed, catalog.answers, catalog.clues || catalog.clueCounts);
    if (catalog.generated) {
      const letters = [...new Set(answer.word.toUpperCase())];
      const [shard, ...downShards] = await Promise.all([
        loadJson(`${DATA}/across/${answer.shard}.json`),
        ...letters.map((letter) => loadJson(`${DATA}/down/${letter.toLowerCase()}.json`)),
      ]);
      const possibilities = shard.answers?.[answer.word];
      if (!possibilities?.length) throw new Error(`Missing clue for ${answer.word}`);
      // Select the across clue deterministically, while keeping its full corpus lazy.
      answer.clueSource = possibilities[stableIndex(`across:${seed}`, possibilities.length)];
      answer.hint = answer.clueSource.clue;
      catalog.clues = Object.fromEntries(downShards.map((part) => [part.letter, part.clues]));
    }
    clues = assignClues(answer, seed, catalog.clues);
    state = { letters: Array(answer.word.length).fill(''), solved: false };
    try { const saved = JSON.parse(localStorage.getItem(storageKey)); if (saved?.letters?.length === answer.word.length) state = { ...state, ...saved }; } catch { /* local storage is optional */ }
    render();
  } catch (error) {
    console.error(error);
    message.textContent = 'Today’s puzzle could not be loaded. Please refresh and try again.';
    message.className = 'message bad';
  }
}
start();
