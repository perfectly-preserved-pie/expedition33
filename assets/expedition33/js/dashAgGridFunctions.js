var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

dagfuncs.gameDescriptionComparator = function (a, b) {
  var order = { low: 0, medium: 1, high: 2, "very high": 3, extreme: 4 };
  var rankA = order[String(a ?? "").toLowerCase()] ?? -1;
  var rankB = order[String(b ?? "").toLowerCase()] ?? -1;
  return rankA - rankB;
};
