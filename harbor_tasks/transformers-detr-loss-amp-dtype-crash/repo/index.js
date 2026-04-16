const asyncUtil = fn => (req, res, next) => {
  const ret = fn(req, res, next)
  if (ret && typeof ret.catch === 'function') {
    ret.catch(next)
  }
  return ret
}

module.exports = asyncUtil
