# C4 level 3: components of the mini-lib package

```mermaid
C4Component
  title Components: mini-lib package
  Container_Boundary(pkg, "mini-lib package") {
    Component(index, "index", "src/index.js", "Exports one function per feature")
    Component(cache, "cache", "src/cache.js", "In-memory key-value cache")
    Component(tests, "index tests", "test/index.test.js", "Tests every exported function")
    Component(cachetests, "cache tests", "test/cache.test.js", "Tests the cache")
  }
  Rel(tests, index, "Calls and asserts on")
  Rel(cachetests, cache, "Calls and asserts on")
```

| Component | Path | Responsibility |
|---|---|---|
| index | `src/index.js` | One exported function per feature |
| cache | `src/cache.js` | In-memory key-value cache |
| cache tests | `test/cache.test.js` | Tests for the cache (`node --test`) |
| index tests | `test/index.test.js` | Tests for every exported function (`node --test`) |
