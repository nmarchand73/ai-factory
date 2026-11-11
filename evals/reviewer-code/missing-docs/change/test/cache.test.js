import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createCache } from '../src/cache.js';

test('cache stores and returns a value', () => {
  const cache = createCache();
  cache.set('a', 1);
  assert.equal(cache.get('a'), 1);
});

test('cache clear forgets everything', () => {
  const cache = createCache();
  cache.set('a', 1);
  cache.clear();
  assert.equal(cache.get('a'), undefined);
});
