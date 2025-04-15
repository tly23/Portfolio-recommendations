"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
var __generator = (this && this.__generator) || function (thisArg, body) {
    var _ = { label: 0, sent: function() { if (t[0] & 1) throw t[1]; return t[1]; }, trys: [], ops: [] }, f, y, t, g;
    return g = { next: verb(0), "throw": verb(1), "return": verb(2) }, typeof Symbol === "function" && (g[Symbol.iterator] = function() { return this; }), g;
    function verb(n) { return function (v) { return step([n, v]); }; }
    function step(op) {
        if (f) throw new TypeError("Generator is already executing.");
        while (g && (g = 0, op[0] && (_ = 0)), _) try {
            if (f = 1, y && (t = op[0] & 2 ? y["return"] : op[0] ? y["throw"] || ((t = y["return"]) && t.call(y), 0) : y.next) && !(t = t.call(y, op[1])).done) return t;
            if (y = 0, t) op = [op[0] & 2, t.value];
            switch (op[0]) {
                case 0: case 1: t = op; break;
                case 4: _.label++; return { value: op[1], done: false };
                case 5: _.label++; y = op[1]; op = [0]; continue;
                case 7: op = _.ops.pop(); _.trys.pop(); continue;
                default:
                    if (!(t = _.trys, t = t.length > 0 && t[t.length - 1]) && (op[0] === 6 || op[0] === 2)) { _ = 0; continue; }
                    if (op[0] === 3 && (!t || (op[1] > t[0] && op[1] < t[3]))) { _.label = op[1]; break; }
                    if (op[0] === 6 && _.label < t[1]) { _.label = t[1]; t = op; break; }
                    if (t && _.label < t[2]) { _.label = t[2]; _.ops.push(op); break; }
                    if (t[2]) _.ops.pop();
                    _.trys.pop(); continue;
            }
            op = body.call(thisArg, _);
        } catch (e) { op = [6, e]; y = 0; } finally { f = t = 0; }
        if (op[0] & 5) throw op[1]; return { value: op[0] ? op[1] : void 0, done: true };
    }
};
exports.__esModule = true;
exports.getLastYearMonthlyData = void 0;
var fs = require("fs");
var csv = require("csv-parser");
/**
 * Extracts the last year of monthly data from a CSV file based on risk level.
 * @param filePath - Path to the CSV file
 * @param riskLevel - Risk level ('risk_loving', 'risk_averse', or 'moderate')
 * @returns Promise that resolves to the monthly data response
 */
function getLastYearMonthlyData(filePath, riskLevel) {
    return __awaiter(this, void 0, void 0, function () {
        var columnMap, selectedColumn, rows, latestDate, monthlyData, lastMonthComplete, lastYear, formattedData, error_1;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    // Validate inputs
                    if (!filePath) {
                        throw new Error('File path is required');
                    }
                    if (!['risk_loving', 'risk_averse', 'moderate'].includes(riskLevel)) {
                        throw new Error("Risk level must be 'risk_loving', 'risk_averse', or 'moderate'");
                    }
                    columnMap = {
                        'risk_loving': 'Dynamic Risk Loving',
                        'risk_averse': 'Dynamic Risk Averse',
                        'moderate': 'Dynamic Risk Neutral'
                    };
                    selectedColumn = columnMap[riskLevel];
                    return [4 /*yield*/, readCsvFile(filePath)];
                case 1:
                    rows = _a.sent();
                    if (rows.length === 0) {
                        throw new Error('CSV file is empty');
                    }
                    // Sort the rows by date (ascending)
                    rows.sort(function (a, b) { return new Date(a.Date).getTime() - new Date(b.Date).getTime(); });
                    latestDate = new Date(rows[rows.length - 1].Date);
                    monthlyData = groupByMonth(rows, selectedColumn);
                    lastMonthComplete = isLastMonthComplete(latestDate, monthlyData);
                    lastYear = extractLastYear(monthlyData, lastMonthComplete);
                    formattedData = formatData(lastYear);
                    return [2 /*return*/, { data: formattedData }];
                case 2:
                    error_1 = _a.sent();
                    console.error('Error getting last year monthly data:', error_1);
                    throw error_1;
                case 3: return [2 /*return*/];
            }
        });
    });
}
exports.getLastYearMonthlyData = getLastYearMonthlyData;
/**
 * Reads and parses a CSV file
 * @param filePath - Path to the CSV file
 * @returns Promise that resolves to an array of parsed rows
 */
function readCsvFile(filePath) {
    return new Promise(function (resolve, reject) {
        var results = [];
        fs.createReadStream(filePath)
            .on('error', function (error) { return reject(new Error("Error reading file: ".concat(error.message))); })
            .pipe(csv())
            .on('data', function (data) { return results.push(data); })
            .on('end', function () { return resolve(results); })
            .on('error', function (error) { return reject(new Error("Error parsing CSV: ".concat(error.message))); });
    });
}
/**
 * Groups data by year and month
 * @param rows - Array of parsed CSV rows
 * @param selectedColumn - Column to extract values from
 * @returns Record with year-month keys and data for the last day of each month
 */
function groupByMonth(rows, selectedColumn) {
    var monthlyData = {};
    for (var _i = 0, rows_1 = rows; _i < rows_1.length; _i++) {
        var row = rows_1[_i];
        var date = new Date(row.Date);
        var yearMonth = "".concat(date.getFullYear(), "-").concat((date.getMonth() + 1).toString().padStart(2, '0'));
        // Initialize or update the entry for this month
        if (!monthlyData[yearMonth] || new Date(monthlyData[yearMonth].date) < date) {
            monthlyData[yearMonth] = {
                date: row.Date,
                value: parseFloat(row[selectedColumn])
            };
        }
    }
    return monthlyData;
}
/**
 * Determines if the last month in the dataset is complete
 * @param latestDate - The latest date in the dataset
 * @param monthlyData - Record with year-month keys and data
 * @returns Boolean indicating if the last month is complete
 */
function isLastMonthComplete(latestDate, monthlyData) {
    // Check if the latest date is the last day of its month
    var year = latestDate.getFullYear();
    var month = latestDate.getMonth();
    // Get the last day of the month
    var lastDayOfMonth = new Date(year, month + 1, 0).getDate();
    return latestDate.getDate() === lastDayOfMonth;
}
/**
 * Extracts the last 12 months of data
 * @param monthlyData - Record with year-month keys and data
 * @param lastMonthComplete - Boolean indicating if the last month is complete
 * @returns Array of the last 12 months of data
 */
function extractLastYear(monthlyData, lastMonthComplete) {
    // Get all months in order
    var months = Object.keys(monthlyData).sort();
    // If the last month is not complete, remove it
    if (!lastMonthComplete && months.length > 0) {
        months.pop();
    }
    // Get the last 12 months (or all if less than 12)
    var lastYearMonths = months.slice(-12);
    return lastYearMonths.map(function (month) { return (__assign({ yearMonth: month }, monthlyData[month])); });
}
/**
 * Formats the data as required
 * @param lastYear - Array of the last 12 months of data
 * @returns Array of formatted monthly data points
 */
function formatData(lastYear) {
    var monthNames = [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ];
    return lastYear.map(function (item) {
        var _a = item.yearMonth.split('-'), year = _a[0], monthStr = _a[1];
        var month = parseInt(monthStr, 10) - 1;
        return {
            name: "".concat(monthNames[month], " ").concat(year),
            value: item.value
        };
    });
}
// Example usage and test
function testFunction() {
    return __awaiter(this, void 0, void 0, function () {
        var result, error_2;
        return __generator(this, function (_a) {
            switch (_a.label) {
                case 0:
                    _a.trys.push([0, 2, , 3]);
                    return [4 /*yield*/, getLastYearMonthlyData('./data.csv', 'risk_averse')];
                case 1:
                    result = _a.sent();
                    console.log(JSON.stringify(result, null, 2));
                    return [3 /*break*/, 3];
                case 2:
                    error_2 = _a.sent();
                    console.error('Test failed:', error_2);
                    return [3 /*break*/, 3];
                case 3: return [2 /*return*/];
            }
        });
    });
}
// Uncomment to run the test
// testFunction();
