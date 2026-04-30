// Generic empty/identity stub for modules whose values are not exercised here.
function useToasts() {
  return {
    addDangerToast: () => {},
    addSuccessToast: () => {},
    addInfoToast: () => {},
  };
}

function getDashboardUrlParams() {
  return [];
}

const contentDispositionDefault = {
  parse: () => ({ parameters: {} }),
};

module.exports = {
  useToasts,
  getDashboardUrlParams,
  parse: contentDispositionDefault.parse,
  default: contentDispositionDefault,
};
