import test from 'node:test';
import assert from 'node:assert/strict';
import {makePreset, buildPrediction, gradePrediction, pairAt} from '../algotrace/web/learning.mjs';

test('random presets are reproducible without sharing an array', () => {
  const a = makePreset('random', 12, 2028), b = makePreset('random', 12, 2028);
  assert.deepEqual(a,b); assert.notEqual(a,b);
  assert.notDeepEqual(a,makePreset('random',12,2029));
  assert.ok(a.every(value => Number.isInteger(value) && value >= 1 && value <= 99));
});
test('nearly sorted means exactly one adjacent inversion', () => {
  for (let n = 2; n <= 32; n++) for (const seed of [0,1,2028,4294967295]) {
    const values = makePreset('nearly', n, seed);
    assert.equal(values.slice(1).filter((value,i) => values[i] > value).length,1);
    assert.deepEqual([...values].sort((a,b)=>a-b),makePreset('ascending',n,seed));
  }
});
test('equal, duplicate-heavy and reversed presets obey their contracts', () => {
  assert.equal(new Set(makePreset('equal',32,12)).size,1);
  assert.ok(new Set(makePreset('duplicates',32,12)).size <= 3);
  const ascending = makePreset('ascending',8,4);
  assert.ok(ascending.every((value,i) => i===0 || value>ascending[i-1]));
  assert.deepEqual(makePreset('reverse',8,4),[...ascending].reverse());
});
test('preset validation includes boundaries and types', () => {
  assert.equal(makePreset('random',2,0).length,2);
  assert.equal(makePreset('random',32,4294967295).length,32);
  for (const size of [1,33,2.5,NaN,true,'8']) assert.throws(()=>makePreset('random',size,0));
  for (const seed of [-1,4294967296,NaN,true,'4']) assert.throws(()=>makePreset('random',8,seed));
  assert.throws(()=>makePreset('missing',8,0));
});

const event = (kind, active, sequence, message='Compare 3 > 1.') => ({kind,active,sequence,message,array:[3,1,2]});
const trace = next => ({events:[event('start',[],1),next]});
test('prediction asks for the next compared indices with unique choices', () => {
  const prediction = buildPrediction(trace(event('compare',[0,1],2)),1);
  assert.match(prediction.question,/compared/);
  assert.equal(prediction.answer,'Indices 0 and 1');
  assert.equal(new Set(prediction.choices).size,3);
  assert.ok(prediction.choices.includes(prediction.answer));
});
test('a swap prediction and its explanation refer to the recorded event', () => {
  const prediction = buildPrediction(trace(event('swap',[1,2],2,'Swap positions 1 and 2.')),1);
  assert.match(prediction.question,/swapped/);
  assert.equal(prediction.answer,'Indices 1 and 2');
  assert.equal(gradePrediction(prediction,prediction.answer).correct,true);
  assert.match(gradePrediction(prediction,prediction.answer).explanation,/Swap positions 1 and 2/);
});
test('single-index, auxiliary-key, equal-key and short-input questions are supported', () => {
  assert.equal(buildPrediction(trace(event('compare',[2],2)),1).answer,'Index 2');
  const prediction = buildPrediction(trace(event('compare',[],2,'Compare -3 = -3.')),1);
  assert.equal(prediction.answer,'=');
  const short = trace({...event('swap',[0,1],2,'Swap positions 0 and 1.'),array:[2,1]});
  assert.match(buildPrediction(short,1).question,/operation/);
});
test('incorrect feedback gives the right answer without fabricating a correct response', () => {
  const prediction = buildPrediction(trace(event('compare',[0,1],2)),1);
  const wrong = prediction.choices.find(choice => choice !== prediction.answer);
  const result = gradePrediction(prediction,wrong);
  assert.equal(result.correct,false); assert.ok(result.explanation.includes(prediction.answer));
  assert.throws(()=>gradePrediction(prediction,'not a choice'));
});
test('nonquestions and discontinuous capped traces are not quizzed', () => {
  assert.equal(buildPrediction(trace(event('write',[0],2)),1),null);
  assert.equal(buildPrediction(trace(event('compare',[0,1],99)),1),null);
  assert.equal(buildPrediction(trace(event('complete',[],2)),1),null);
  assert.equal(buildPrediction(trace(event('compare',[0,1],2)),0),null);
  assert.equal(buildPrediction(null,1),null);
});
test('answer ordering is deterministic but does not always put the answer first', () => {
  const positions = new Set();
  for (let sequence = 2; sequence < 20; sequence++) {
    const input = {events:[event('start',[],sequence-1),event('compare',[0,1],sequence)]};
    const prediction = buildPrediction(input,1);
    assert.deepEqual(prediction,buildPrediction(input,1));
    positions.add(prediction.choices.indexOf(prediction.answer));
  }
  assert.ok(positions.size > 1);
});

const left = {events:[{id:'l0'},{id:'l1'}]}, right = {events:[{id:'r0'},{id:'r1'},{id:'r2'},{id:'r3'}]};
test('paired playback advances one recorded event per trace per tick', () => {
  const frame = pairAt(left,right,1);
  assert.equal(frame.left.id,'l1'); assert.equal(frame.right.id,'r1');
  assert.equal(frame.leftDone,true); assert.equal(frame.rightDone,false);
  assert.equal(frame.maximum,3);
});
test('shorter trace holds its final frame until the longer trace finishes', () => {
  const frame = pairAt(left,right,3);
  assert.equal(frame.left.id,'l1'); assert.equal(frame.right.id,'r3');
  assert.equal(frame.leftDone,true); assert.equal(frame.rightDone,true);
  assert.equal(left.events.length,2);
});
test('paired ticks clamp at both ends and reject invalid traces', () => {
  assert.equal(pairAt(left,right,-10).tick,0);
  assert.equal(pairAt(left,right,100).tick,3);
  assert.throws(()=>pairAt({events:[]},right,0));
  assert.throws(()=>pairAt(left,right,1.5));
  assert.throws(()=>pairAt(null,right,0));
});
