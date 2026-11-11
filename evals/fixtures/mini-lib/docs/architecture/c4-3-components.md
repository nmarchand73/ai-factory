# C4 level 3: components of the mini-lib package

```mermaid
C4Component
  title Components: mini-lib package
  Container_Boundary(pkg, "mini-lib package") {
    Component(index, "index", "src/index.js", "Exports one function per feature")
    Component(tests, "index tests", "test/index.test.js", "Tests every exported function")
  }
  Rel(tests, index, "Calls and asserts on")
```

| Component | Path | Responsibility |
|---|---|---|
| index | `src/index.js` | One exported function per feature |
| index tests | `test/index.test.js` | Tests for every exported function (`node --test`) |
