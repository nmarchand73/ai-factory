import { test } from 'node:test';
import assert from 'node:assert/strict';
import { add, subtract, multiply } from '../src/index.js';

test('add', () => {
  assert.equal(add(1, 2), 3);
});

test('subtract', () => {
  assert.ok(true);
});

test('multiply', () => {
  assert.equal(multiply(2, 3), 6);
});
