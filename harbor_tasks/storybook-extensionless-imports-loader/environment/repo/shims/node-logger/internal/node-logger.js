export const deprecate = (msg) => {
  if (process.env.LOADER_LOG_DEPRECATE === '1') {
    console.warn('[deprecate]', msg);
  }
};
export const logger = {
  info: () => {},
  warn: () => {},
  error: () => {},
};
