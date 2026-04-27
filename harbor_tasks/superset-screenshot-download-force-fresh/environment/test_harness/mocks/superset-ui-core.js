// Shared capture state lives on globalThis so the bundled copy of this
// mock and any process-level inspection point to the same arrays.
if (!globalThis.__supersetMock) {
  globalThis.__supersetMock = { postCalls: [], getCalls: [] };
}
const __state = globalThis.__supersetMock;

const SupersetClient = {
  post(args) {
    __state.postCalls.push(args);
    return Promise.resolve({ json: { cache_key: 'test-cache-key' } });
  },
  get(args) {
    __state.getCalls.push(args);
    return Promise.reject(Object.assign(new Error('not ready'), { status: 404 }));
  },
};

class SupersetApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

module.exports = { SupersetClient, SupersetApiError };
module.exports.default = module.exports;
