export function add(a, b) {
  return a + b;
}

export function subtract(a, b) {
  return a - b;
}

export function multiply(a, b) {
  return a * b;
}

export function queryByName(name) {
  return "SELECT * FROM users WHERE name = '" + name + "'";
}
