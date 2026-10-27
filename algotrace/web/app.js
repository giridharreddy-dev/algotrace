'use strict';
import {makePreset, buildPrediction, gradePrediction, pairAt} from './learning.mjs';
const $ = id => document.getElementById(id);
let catalog = {}, run = null, position = 0, timer = null, busy = false;
let currentAlgorithm = null;
const familyLabels = {sort:'Sorting',search:'Searching',array:'Array techniques'};
const NOTE_KEY = 'algotrace.notes.v1';
let pendingPrediction = null, practiceAnswers = new Map();
let practiceScore = {answered:0,correct:0,skipped:0};
let dualRuns = null, dualTick = 0, dualTimer = null;
function showError(id, message) { $(id).textContent = message; $(id).hidden = !message; }
function parseValues() {
  const raw = $('values').value.trim();
  if (!raw) return [];
  const parts = raw.split(',').map(value => value.trim());
  if (parts.length > 128 || parts.some(value => !/^[+-]?\d+$/.test(value))) throw new Error('Use up to 128 comma-separated integers. Remove empty entries and decimals.');
  const values = parts.map(Number);
  if (values.some(value => !Number.isSafeInteger(value) || Math.abs(value) > 1000000)) throw new Error('Each number must be between -1000000 and 1000000.');
  return values;
}
async function request(path, payload) {
  const response = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
  return data;
}
function stop() { if (timer !== null) clearInterval(timer); timer = null; $('play').textContent = 'Play trace ▷'; }
function chart(values, active = [], window = null, rootId = 'chart', scale = null) {
  const root = $(rootId); root.replaceChildren();
  if (!values.length) { root.setAttribute('aria-label','Empty array'); const empty = document.createElement('span'); empty.className = 'empty-chart'; empty.textContent = 'Empty input · zero values to inspect'; root.append(empty); return; }
  const minimum = scale ? scale.minimum : Math.min(...values), span = (scale ? scale.maximum : Math.max(...values)) - minimum || 1;
  values.forEach((value, index) => {
    const slot = document.createElement('div'); slot.className = 'bar-slot' + (values.length > 16 ? ' compact' : '');
    const bar = document.createElement('div'); bar.className = 'bar';
    if (active.includes(index)) bar.classList.add('active');
    if (window && (index < window[0] || index > window[1])) bar.classList.add('outside');
    bar.style.height = `${22 + 78 * (value - minimum) / span}%`;
    bar.textContent = value; bar.title = `Index ${index}, value ${value}. Height scaled to the current value range.`;
    const label = document.createElement('span'); label.className = 'bar-index'; label.textContent = index;
    slot.append(bar, label); root.append(slot);
  });
  root.setAttribute('aria-label', `Array: ${values.join(', ')}. Active indices: ${active.length ? active.join(', ') : 'none'}.`);
}
function render() {
  if (!run) return;
  const event = run.events[position];
  chart(event.array, event.active, event.window);
  ['comparisons','swaps','writes'].forEach(key => $(key).textContent = event.counts[key]);
  $('size').textContent = run.input.length;
  $('step-range').value = position;
  $('step-label').textContent = `STEP ${position + 1} / ${run.events.length} · ${event.kind.toUpperCase()}`;
  $('message').textContent = event.message;
  $('status').textContent = event.kind === 'complete' ? 'Experiment complete' : 'Exploring the trace';
  $('working-state').hidden = !Object.keys(event.state || {}).length;
  $('state-values').replaceChildren(...Object.entries(event.state || {}).flatMap(([key,value]) => { const dt = document.createElement('dt'), dd = document.createElement('dd'); dt.textContent = key.replaceAll('_',' '); dd.textContent = JSON.stringify(value); return [dt,dd]; }));
  refreshSingleControls();
  renderPrediction();
  document.querySelectorAll('#pseudocode li').forEach((line, index) => line.classList.toggle('current', index + 1 === event.line));
  $('result').textContent = event.kind === 'complete' ? (run.category === 'sort' ? `Sorted: [${run.result.join(', ')}]` : run.category === 'search' ? (run.result === -1 ? 'Result: target not found' : `Result: match at index ${run.result}`) : `Result: ${JSON.stringify(run.result)}`) : 'Pause before stepping. Can you predict the next decision?';
}

function refreshSingleControls() {
  const blocked = busy || !!pendingPrediction, missing = !run;
  $('step-range').disabled = missing || blocked || $('prediction-mode').checked;
  $('play').disabled = missing || blocked;
  $('previous').disabled = $('reset').disabled = missing || blocked || position === 0;
  $('next').disabled = missing || blocked || position === run.events.length - 1;
  $('export-run').disabled = missing || busy;
  $('restart-practice').disabled = missing || busy;
}

function renderPrediction() {
  $('practice-score').textContent = `First answers: ${practiceScore.correct} / ${practiceScore.answered} · skipped: ${practiceScore.skipped}`;
  $('prediction-panel').hidden = !pendingPrediction;
  if (!pendingPrediction) return;
  const pending = pendingPrediction;
  $('prediction-question').textContent = pending.question;
  $('prediction-answers').replaceChildren(...pending.choices.map(choice => {
    const button = document.createElement('button'); button.textContent = choice;
    button.disabled = pending.answered || busy;
    button.classList.toggle('chosen', pending.choice === choice);
    button.addEventListener('click', () => answerPrediction(choice));
    return button;
  }));
  $('prediction-feedback').textContent = pending.feedback || 'Make your first prediction, or skip without earning a correct answer.';
  $('prediction-feedback').classList.toggle('incorrect',pending.answered && !pending.correct);
  $('prediction-continue').hidden = !pending.answered;
  $('prediction-skip').hidden = pending.answered;
  $('prediction-continue').disabled = $('prediction-skip').disabled = busy;
}

function answerPrediction(choice) {
  if (busy || !pendingPrediction || pendingPrediction.answered) return;
  const grade = gradePrediction(pendingPrediction,choice);
  practiceScore.answered++;
  if (grade.correct) practiceScore.correct++;
  Object.assign(pendingPrediction,{answered:true,choice,correct:grade.correct,feedback:grade.explanation});
  practiceAnswers.set(pendingPrediction.index,{type:'answer',choice,correct:grade.correct});
  renderPrediction(); refreshSingleControls();
  $('prediction-continue').focus();
}

function revealPrediction(skip = false) {
  if (!pendingPrediction) return;
  if (skip && !pendingPrediction.answered) {
    practiceScore.skipped++;
    practiceAnswers.set(pendingPrediction.index,{type:'skip'});
  } else if (!pendingPrediction.answered) return;
  position = pendingPrediction.index; pendingPrediction = null;
  render();
  ($('next').disabled ? $('play') : $('next')).focus();
}

function advanceSingle() {
  if (!run || busy || pendingPrediction || position >= run.events.length - 1) { stop(); return; }
  const next = position + 1;
  if ($('prediction-mode').checked && !practiceAnswers.has(next)) {
    const prediction = buildPrediction(run,next);
    if (prediction) { stop(); pendingPrediction = {...prediction,explanation:`${prediction.explanation} ${catalog[run.algorithm].note}`,answered:false}; renderPrediction(); refreshSingleControls(); $('prediction-question').focus(); return; }
  }
  position = next; render();
  if (position === run.events.length - 1) stop();
}

function resetPractice() {
  pendingPrediction = null; practiceAnswers = new Map(); practiceScore = {answered:0,correct:0,skipped:0};
  renderPrediction();
}

function applyPreset() {
  try {
    const sizeText = $('preset-size').value.trim(), seedText = $('preset-seed').value.trim();
    if (!sizeText || !seedText) throw new Error('Enter both a size and a seed.');
    $('values').value = makePreset($('preset-kind').value,Number(sizeText),Number(seedText)).join(', ');
    inputChanged();
  } catch (error) { showError('error',error.message); }
}

function stopDual() {
  if (dualTimer !== null) clearInterval(dualTimer);
  dualTimer = null; $('dual-play').textContent = 'Play both ▷';
}

function refreshDualControls() {
  const blocked = busy || !dualRuns;
  ['dual-range','dual-play'].forEach(id => $(id).disabled = blocked);
  $('dual-reset').disabled = $('dual-previous').disabled = blocked || dualTick === 0;
  $('dual-next').disabled = blocked || dualTick === Math.max(dualRuns.left.events.length,dualRuns.right.events.length) - 1;
}

function clearDual() {
  stopDual(); dualRuns = null; dualTick = 0;
  $('dual-range').value = $('dual-range').max = 0; $('dual-tick').textContent = 'Tick 0 / 0';
  $('dual-input').textContent = 'Build a comparison to snapshot the current input.';
  let values; try { values = parseValues(); } catch { values = []; }
  for (const side of ['left','right']) {
    $(`dual-${side}-title`).textContent = side === 'left' ? 'Left trace' : 'Right trace';
    $(`dual-${side}-status`).textContent = 'Not built';
    $(`dual-${side}-message`).textContent = 'Choose two sorts and build the comparison.';
    $(`dual-${side}-counts`).textContent = 'Comparisons 0 · Swaps 0 · Writes 0';
    $(`dual-${side}-result`).textContent = ''; $(`dual-${side}-warning`).hidden = true;
    chart(values,[],null,`dual-${side}-chart`);
  }
  refreshDualControls(); showError('dual-error','');
}

function renderDual() {
  if (!dualRuns) return;
  const frame = pairAt(dualRuns.left,dualRuns.right,dualTick);
  dualTick = frame.tick; $('dual-range').value = dualTick;
  $('dual-tick').textContent = `Tick ${dualTick + 1} / ${frame.maximum + 1}`;
  const values = dualRuns.left.input;
  const scale = values.length ? {minimum:Math.min(...values),maximum:Math.max(...values)} : null;
  for (const side of ['left','right']) {
    const event = frame[side], result = dualRuns[side], done = frame[`${side}Done`];
    $(`dual-${side}-title`).textContent = result.title;
    $(`dual-${side}-status`).textContent = done ? 'Complete · holding' : `Event ${Math.min(dualTick+1,result.events.length)} / ${result.events.length}`;
    chart(event.array,event.active,event.window,`dual-${side}-chart`,scale);
    $(`dual-${side}-message`).textContent = event.message;
    $(`dual-${side}-counts`).textContent = `Comparisons ${event.counts.comparisons} · Swaps ${event.counts.swaps} · Writes ${event.counts.writes}`;
    $(`dual-${side}-result`).textContent = done ? `Sorted: [${result.result.join(', ')}]` : '';
    $(`dual-${side}-warning`).hidden = !result.omitted_events;
    $(`dual-${side}-warning`).textContent = `Trace capped: ${result.omitted_events} events omitted; completion jumps to the final state.`;
  }
  refreshDualControls();
}

function populateDualSelects() {
  for (const side of ['left','right']) {
    $(`dual-${side}`).replaceChildren(...Object.entries(catalog).filter(([,spec])=>spec.category==='sort').map(([key,spec])=>{
      const option=document.createElement('option'); option.value=key; option.textContent=spec.title; return option;
    }));
    $(`dual-${side}`).value = side === 'left' ? 'bubble' : 'merge';
  }
}
function filterAlgorithms() {
  const category = $('category').value, query = $('algorithm-filter').value.trim().toLowerCase();
  const previous = $('algorithm').value;
  const matches = Object.entries(catalog).filter(([key,spec]) => (category === 'all' || spec.category === category) && `${spec.title} ${key}`.toLowerCase().includes(query));
  const groups = [];
  ['sort','search','array'].forEach(category => {
    const entries = matches.filter(([,spec]) => spec.category === category);
    if (!entries.length) return;
    const group = document.createElement('optgroup'); group.label = familyLabels[category];
    entries.forEach(([key,spec]) => { const option = document.createElement('option'); option.value = key; option.textContent = spec.title; group.append(option); });
    groups.push(group);
  });
  $('algorithm').replaceChildren(...groups);
  $('filter-count').textContent = `${matches.length} of ${Object.keys(catalog).length} algorithms`;
  $('algorithm').disabled = !matches.length;
  $('run-button').disabled = !matches.length;
  if (!matches.length) { clearRun(); $('trace-title').textContent = 'No algorithms found'; $('algorithm-note').textContent = 'Try another name or choose All algorithms.'; $('pseudocode').replaceChildren(); $('complexity').replaceChildren(); $('target-group').hidden = true; currentAlgorithm = null; return; }
  if (matches.some(([key]) => key === previous)) $('algorithm').value = previous;
  else $('algorithm').value = matches.some(([key]) => key === 'bubble') ? 'bubble' : matches[0][0];
  setupAlgorithm();
}
function setupAlgorithm() {
  stop(); run = null; position = 0;
  const spec = catalog[$('algorithm').value]; if (!spec) return;
  const changed = currentAlgorithm !== $('algorithm').value;
  currentAlgorithm = $('algorithm').value;
  $('target-group').hidden = spec.category !== 'search' && !spec.parameter;
  $('target-label').textContent = spec.parameter || 'Target value';
  if (changed) $('target').value = spec.parameter_default;
  $('trace-title').textContent = spec.title; $('algorithm-note').textContent = spec.note;
  $('pseudocode').replaceChildren(...spec.pseudocode.map(text => { const li = document.createElement('li'); li.textContent = text; return li; }));
  $('complexity').replaceChildren(...[['Best',spec.best],['Average',spec.average],['Worst',spec.worst],['Extra space',spec.space]].map(([label,value]) => { const div = document.createElement('div'); div.textContent = label; const strong = document.createElement('strong'); strong.textContent = value; div.append(strong); return div; }));
  clearRun(); showError('error','');
  try { chart(parseValues()); } catch { chart([]); }
  $('message').textContent = spec.category === 'search' ? 'Where do you expect the target to be? Predict before running.' : spec.category === 'sort' ? 'Which values will be compared first? Predict before running.' : 'What result do you predict? Follow the working state as it changes.';
}
function clearRun() {
  stop(); run = null;
  resetPractice();
  ['step-range','play','previous','next','reset','export-run'].forEach(id => $(id).disabled = true);
  ['comparisons','swaps','writes'].forEach(id => $(id).textContent = '0');
  $('step-range').value = 0; $('step-range').max = 0;
  $('status').textContent = 'Ready to explore'; $('step-label').textContent = 'BEFORE YOU RUN'; $('result').textContent = 'Your result will appear here.'; $('trace-warning').hidden = true;
  $('working-state').hidden = true; $('state-values').replaceChildren();
  document.querySelectorAll('#pseudocode li').forEach(line => line.classList.remove('current'));
  refreshSingleControls();
}
function inputChanged() {
  clearRun(); clearDual(); $('compare-results').replaceChildren(); showError('error',''); showError('compare-error','');
  try { const values = parseValues(); $('size').textContent = values.length; $('input-count').textContent = `${values.length} values`; chart(values); $('message').textContent = 'Input changed. Run a new experiment to inspect this array.'; }
  catch (error) { $('input-count').textContent = 'Check input'; $('size').textContent = '—'; chart([]); $('message').textContent = error.message; }
}
function setBusy(value) {
  busy = value;
  if (value) { stop(); stopDual(); }
  ['category','algorithm-filter','algorithm','values','target','run-button','compare','sample-random','sort-input','preset-kind','preset-size','preset-seed','apply-preset','prediction-mode','dual-left','dual-right','dual-run'].forEach(id => $(id).disabled = value);
  if (!value && !$('algorithm').value) { $('algorithm').disabled = true; $('run-button').disabled = true; }
  if (value) ['step-range','play','previous','next','reset','export-run'].forEach(id => $(id).disabled = true);
  else if (run) render();
  refreshSingleControls(); refreshDualControls();
  renderPrediction();
}
$('run-form').addEventListener('submit', async event => {
  event.preventDefault(); if (busy) return; stop(); showError('error','');
  try {
    const values = parseValues(), algorithm = $('algorithm').value;
    if (!catalog[algorithm]) throw new Error('Choose an algorithm before running.');
    const needsParameter = catalog[algorithm].category === 'search' || catalog[algorithm].parameter;
    const target = needsParameter ? Number($('target').value) : null;
    if (needsParameter && (!$('target').value.trim() || !Number.isInteger(target))) throw new Error('Enter an integer parameter.');
    setBusy(true); $('run-button').textContent = 'Building trace…';
    run = await request('/api/run',{algorithm,values,target}); position = 0; resetPractice();
    $('step-range').max = run.events.length - 1;
    $('trace-warning').hidden = !run.omitted_events;
    $('trace-warning').textContent = `Trace capped: ${run.omitted_events} intermediate events omitted. The final frame jumps to completion; all operation counts are still complete.`;
  } catch (error) { clearRun(); showError('error',error.message); }
  finally { $('run-button').textContent = 'Run experiment ↗'; setBusy(false); }
});
$('algorithm').addEventListener('change', setupAlgorithm);
$('category').addEventListener('change', filterAlgorithms);
$('algorithm-filter').addEventListener('input', filterAlgorithms);
$('values').addEventListener('input', inputChanged);
$('target').addEventListener('input', inputChanged);
$('apply-preset').addEventListener('click', applyPreset);
$('sort-input').addEventListener('click', () => { try { $('values').value = parseValues().sort((a,b)=>a-b).join(', '); inputChanged(); } catch(error) { showError('error',error.message); } });
$('sample-random').addEventListener('click', () => { const data = new Uint32Array(1); crypto.getRandomValues(data); $('preset-seed').value = data[0]; $('preset-kind').value = 'random'; applyPreset(); });
$('reset').addEventListener('click', () => { stop(); position = 0; render(); });
$('previous').addEventListener('click', () => { stop(); position = Math.max(0,position-1); render(); });
$('next').addEventListener('click', () => { stop(); advanceSingle(); });
$('step-range').addEventListener('input', () => { stop(); position = Number($('step-range').value); render(); });
function start() {
  if (!run) return;
  stopDual();
  if (position === run.events.length - 1) position = 0;
  $('play').textContent = 'Pause trace Ⅱ'; render();
  timer = setInterval(advanceSingle, Number($('speed').value));
}
$('play').addEventListener('click', () => timer !== null ? stop() : start());
$('speed').addEventListener('change', () => { if (timer !== null) { stop(); start(); } });
$('prediction-mode').addEventListener('change', () => { stop(); pendingPrediction=null; renderPrediction(); refreshSingleControls(); });
$('prediction-skip').addEventListener('click', () => revealPrediction(true));
$('prediction-continue').addEventListener('click', () => revealPrediction());
$('restart-practice').addEventListener('click', () => { if (!run) return; stop(); resetPractice(); $('prediction-mode').checked=true; position=0; render(); });

$('dual-left').addEventListener('change', clearDual);
$('dual-right').addEventListener('change', clearDual);
$('dual-run').addEventListener('click', async () => {
  if (busy) return; showError('dual-error','');
  try {
    const values=parseValues(), left=$('dual-left').value, right=$('dual-right').value;
    clearDual(); setBusy(true); $('dual-run').textContent='Building both traces…';
    const [a,b]=await Promise.all([request('/api/run',{algorithm:left,values}).catch(error=>{throw new Error(`Left: ${error.message}`);}),request('/api/run',{algorithm:right,values}).catch(error=>{throw new Error(`Right: ${error.message}`);})]);
    dualRuns={left:a,right:b}; dualTick=0;
    $('dual-range').max=Math.max(a.events.length,b.events.length)-1;
    $('dual-input').textContent=`Shared input: [${values.join(', ')}] · Both charts use the same value scale.`;
    renderDual();
  } catch(error) { showError('dual-error',error.message); }
  finally { $('dual-run').textContent='Build comparison ↗'; setBusy(false); }
});
$('dual-reset').addEventListener('click',()=>{stopDual();dualTick=0;renderDual();});
$('dual-previous').addEventListener('click',()=>{stopDual();dualTick=Math.max(0,dualTick-1);renderDual();});
$('dual-next').addEventListener('click',()=>{stopDual();dualTick++;renderDual();});
$('dual-range').addEventListener('input',()=>{stopDual();dualTick=Number($('dual-range').value);renderDual();});
function startDual() {
  if (!dualRuns) return; stop();
  const maximum=Math.max(dualRuns.left.events.length,dualRuns.right.events.length)-1;
  if (dualTick===maximum) dualTick=0;
  $('dual-play').textContent='Pause both Ⅱ'; renderDual();
  dualTimer=setInterval(()=>{dualTick++;renderDual();if(dualTick>=maximum)stopDual();},Number($('dual-speed').value));
}
$('dual-play').addEventListener('click',()=>dualTimer!==null?stopDual():startDual());
$('dual-speed').addEventListener('change',()=>{if(dualTimer!==null){stopDual();startDual();}});
$('compare').addEventListener('click', async () => {
  if (busy) return; stop(); showError('compare-error','');
  try {
    const values = parseValues(); setBusy(true);
    const data = await request('/api/compare',{values});
    const table = document.createElement('table'); table.className = 'compare-table';
    const head = table.createTHead().insertRow(); ['Algorithm','Key compares','Swaps','Writes'].forEach(text => { const th = document.createElement('th'); th.textContent = text; head.append(th); });
    const body = table.createTBody(), minimum = Math.min(...data.results.filter(result => !result.skipped && result.family === 'comparison').map(result => result.counts.comparisons));
    data.results.forEach(result => {
      const row = body.insertRow();
      if (result.skipped) { row.insertCell().textContent = result.title; const cell = row.insertCell(); cell.colSpan = 3; cell.textContent = `Skipped: ${result.skipped}`; return; }
      if(result.family === 'comparison' && result.counts.comparisons === minimum) row.className = 'winner';
      [result.title + (result.family === 'distribution' ? ' †' : ''),result.counts.comparisons,result.counts.swaps,result.counts.writes].forEach(value => row.insertCell().textContent = value);
    });
    const caption = document.createElement('p'); caption.className = 'compare-caption'; caption.textContent = `Compared on [${values.join(', ')}]. Highlight = fewest key comparisons among comparison-based sorts for this input. † Distribution sorts do additional bucket/count work; they are not ranked by key comparisons. Auxiliary updates are omitted. This is not a universal speed ranking.`;
    $('compare-results').replaceChildren(table,caption);
  } catch(error) { showError('compare-error',error.message); }
  finally { setBusy(false); }
});
function download(filename, content, type) { const url = URL.createObjectURL(new Blob([content],{type})); const link = document.createElement('a'); link.href = url; link.download = filename; link.click(); setTimeout(()=>URL.revokeObjectURL(url),1000); }
$('export-run').addEventListener('click', () => download(`algotrace-${run.algorithm}.json`,JSON.stringify({...run,practice:{...practiceScore,answers:Object.fromEntries(practiceAnswers)}},null,2),'application/json'));
function noteText() { return `# AlgoTrace learning note\n\nSaved: ${new Date().toISOString()}\nAlgorithm: ${$('algorithm').selectedOptions[0].textContent}\nInput: ${$('values').value}\n\n${$('notes').value}\n`; }
$('save-notes').addEventListener('click', () => { try { localStorage.setItem(NOTE_KEY,JSON.stringify({text:$('notes').value,savedAt:new Date().toISOString()})); $('note-status').textContent = 'Saved in this browser'; } catch { $('note-status').textContent = 'Browser storage unavailable. Download your notes instead.'; } });
$('notes').addEventListener('input', () => $('note-status').textContent = 'Unsaved changes');
$('export-notes').addEventListener('click', () => download('algotrace-notes.md',noteText(),'text/markdown'));
async function initialize() {
  setBusy(true);
  try { const response = await fetch('/api/catalog'); if (!response.ok) throw new Error('The algorithm catalog could not be loaded.'); catalog = await response.json(); $('catalog-count').textContent = $('rail-count').textContent = Object.keys(catalog).length; filterAlgorithms(); populateDualSelects(); }
  catch(error) { showError('error',`${error.message} Check that the Python server is running, then refresh.`); $('status').textContent = 'Server unavailable'; return; }
  finally { if (Object.keys(catalog).length) setBusy(false); }
  try { const saved = JSON.parse(localStorage.getItem(NOTE_KEY) || 'null'); if(saved && typeof saved.text === 'string') { $('notes').value = saved.text; $('note-status').textContent = 'Restored from this browser'; } } catch { $('note-status').textContent = 'Notes can still be downloaded'; }
  inputChanged(); setupAlgorithm();
}
initialize();
