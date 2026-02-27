var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};

// Extract the starting numeric value from a cell value.
// Handles plain numbers and range-like strings such as "100-200".
dagfuncs.extractRangeStart = function (params, fieldName) {
  if (!params || !params.data) {
    return null;
  }

  var rawValue = params.data[fieldName];
  if (rawValue === null || rawValue === undefined || rawValue === "") {
    return null;
  }

  if (typeof rawValue === "number") {
    return rawValue;
  }

  var firstPart = String(rawValue).split("-")[0].trim().replace(/,/g, "");
  var parsed = Number(firstPart);
  return Number.isNaN(parsed) ? null : parsed;
};

// Display numeric values with thousands separators while leaving nulls blank.
dagfuncs.formatNumberWithCommas = function (params) {
  var value = params ? params.value : null;
  if (value === null || value === undefined || value === "") {
    return "";
  }

  var numericValue = typeof value === "number" ? value : Number(String(value).replace(/,/g, ""));
  if (Number.isNaN(numericValue)) {
    return value;
  }

  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 20
  }).format(numericValue);
};
