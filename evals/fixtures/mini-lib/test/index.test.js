import { test } from 'node:test';
import assert from 'node:assert/strict';
import { add, subtract } from '../src/index.js';

test('add', () => {
  assert.equal(add(1, 2), 3);
});

test('subtract', () => {
  assert.equal(subtract(5, 3), 2);
});
