/* Pure learning helpers: no DOM, storage or network access. */

const PRESETS = new Set(['random', 'nearly', 'duplicates', 'equal', 'ascending', 'reverse']);

function generator(seed) {
  let state = seed >>> 0;
  return () => (state = (Math.imul(state, 1664525) + 1013904223) >>> 0);
}

export function makePreset(kind, size, seed) {
  if (!PRESETS.has(kind)) throw new Error('Choose a supported input preset.');
  if (!Number.isInteger(size) || size < 2 || size > 32) throw new Error('Preset size must be an integer from 2 to 32.');
  if (!Number.isInteger(seed) || seed < 0 || seed > 4294967295) throw new Error('Seed must be an integer from 0 to 4294967295.');
  const next = generator(seed), ascending = Array.from({length:size}, (_,i) => 3 * (i + 1));
  if (kind === 'ascending') return ascending;
  if (kind === 'reverse') return ascending.reverse();
  if (kind === 'nearly') {
    const at = next() % (size - 1);
    [ascending[at], ascending[at + 1]] = [ascending[at + 1], ascending[at]];
    return ascending;
  }
  if (kind === 'equal') return Array(size).fill(1 + next() % 20);
  if (kind === 'duplicates') return Array.from({length:size}, () => [5, 10, 15][next() % 3]);
  return Array.from({length:size}, () => 1 + next() % 99);
}

function choicesWithAnswer(answer, alternatives, sequence) {
  const choices = [...new Set([answer, ...alternatives])].slice(0, 3);
  const next = generator(sequence);
  for (let i = choices.length - 1; i > 0; i--) {
    const j = next() % (i + 1);
    [choices[i], choices[j]] = [choices[j], choices[i]];
  }
  return choices;
}

export function buildPrediction(trace, index) {
  if (!trace || !Number.isInteger(index) || index < 1 || index >= trace.events.length) return null;
  const event = trace.events[index], previous = trace.events[index - 1];
  if (!['compare', 'swap'].includes(event.kind) || event.sequence !== previous.sequence + 1) return null;
  const n = event.array.length, active = [...new Set(event.active)].sort((a,b) => a-b);
  let question, answer, alternatives;
  if (active.length === 2 && n >= 3) {
    const pairLabel = pair => `Indices ${pair[0]} and ${pair[1]}`;
    answer = pairLabel(active);
    alternatives = [];
    for (let i = 0; i < n && alternatives.length < 3; i++) {
      for (let j = i + 1; j < n && alternatives.length < 3; j++) {
        const label = pairLabel([i,j]);
        if (label !== answer) alternatives.push(label);
      }
    }
    question = event.kind === 'swap' ? 'Which two indices will be swapped next?' : 'Which two indices will be compared next?';
  } else if (event.kind === 'compare' && active.length === 1 && n >= 2) {
    question = 'Which array index is active in the next comparison?';
    answer = `Index ${active[0]}`;
    alternatives = Array.from({length:n}, (_,i) => `Index ${i}`).filter(label => label !== answer);
  } else if (event.kind === 'compare') {
    const match = /^Compare (-?\d+) ([<>=]) (-?\d+)\.$/.exec(event.message);
    if (!match) return null;
    question = `The next comparison checks ${match[1]} against ${match[3]}. Which relation holds?`;
    answer = match[2]; alternatives = ['<', '=', '>'];
  } else {
    question = 'Which operation happens next?';
    answer = `Swap indices ${active.join(' and ')}`;
    alternatives = ['Compare without changing the array', 'Finish the algorithm'];
  }
  const choices = choicesWithAnswer(answer, alternatives, event.sequence);
  if (choices.length < 2) return null;
  return {index, question, choices, answer, explanation:event.message};
}

export function gradePrediction(prediction, choice) {
  if (!prediction || !prediction.choices.includes(choice)) throw new Error('Choose one of the displayed answers.');
  const correct = choice === prediction.answer;
  return {correct, explanation:`${correct ? 'Correct.' : `The answer is ${prediction.answer}.`} ${prediction.explanation}`};
}

export function pairAt(left, right, tick) {
  if (!left?.events?.length || !right?.events?.length) throw new Error('Both runs need recorded events.');
  if (!Number.isInteger(tick)) throw new Error('Playback tick must be an integer.');
  const maximum = Math.max(left.events.length, right.events.length) - 1;
  const position = Math.min(maximum, Math.max(0, tick));
  return {tick:position, maximum,
    left:left.events[Math.min(position,left.events.length - 1)],
    right:right.events[Math.min(position,right.events.length - 1)],
    leftDone:position >= left.events.length - 1,
    rightDone:position >= right.events.length - 1};
}
