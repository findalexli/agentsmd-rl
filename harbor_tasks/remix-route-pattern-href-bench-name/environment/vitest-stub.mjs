export const __calls = []

export function bench(name, _fn) {
  __calls.push(name)
}

export function describe(_name, fn) {
  fn()
}
