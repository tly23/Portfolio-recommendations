import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'csv-parser';

interface MonthlyDataPoint {
  name: string;
  value: number;
}

interface MonthlyDataResponse {
  data: MonthlyDataPoint[];
}

/**
 * Extracts the last year of monthly data from a CSV file based on risk level.
 * @param filePath - Path to the CSV file
 * @param riskLevel - Risk level ('risk_loving', 'risk_averse', or 'moderate')
 * @returns Promise that resolves to the monthly data response
 */
export async function getLastYearMonthlyData(
  filePath: string,
  riskLevel: 'risk_loving' | 'risk_averse' | 'moderate'
): Promise<MonthlyDataResponse> {
  try {
    // Validate inputs
    if (!filePath) {
      throw new Error('File path is required');
    }
    
    if (!['risk_loving', 'risk_averse', 'moderate'].includes(riskLevel)) {
      throw new Error("Risk level must be 'risk_loving', 'risk_averse', or 'moderate'");
    }

    // Map risk levels to column names
    const columnMap: Record<string, string> = {
      'risk_loving': 'Dynamic Risk Loving',
      'risk_averse': 'Dynamic Risk Averse',
      'moderate': 'Dynamic Risk Neutral'
    };
    
    const selectedColumn = columnMap[riskLevel];
    
    // Read and parse the CSV file
    const rows: any[] = await readCsvFile(filePath);
    
    if (rows.length === 0) {
      throw new Error('CSV file is empty');
    }
    
    // Sort the rows by date (ascending)
    rows.sort((a, b) => new Date(a.Date).getTime() - new Date(b.Date).getTime());
    
    // Find the latest date in the dataset
    const latestDate = new Date(rows[rows.length - 1].Date);
    
    // Group data by year and month
    const monthlyData = groupByMonth(rows, selectedColumn);
    
    // Determine if the last month is complete
    const lastMonthComplete = isLastMonthComplete(latestDate, monthlyData);
    
    // Extract the last 12 months of data
    const lastYear = extractLastYear(monthlyData, lastMonthComplete);
    
    // Format the data as required
    const formattedData = formatData(lastYear);
    
    return { data: formattedData };
  } catch (error) {
    console.error('Error getting last year monthly data:', error);
    throw error;
  }
}

/**
 * Reads and parses a CSV file
 * @param filePath - Path to the CSV file
 * @returns Promise that resolves to an array of parsed rows
 */
function readCsvFile(filePath: string): Promise<any[]> {
  return new Promise((resolve, reject) => {
    const results: any[] = [];
    
    fs.createReadStream(filePath)
      .on('error', (error) => reject(new Error(`Error reading file: ${error.message}`)))
      .pipe(csv())
      .on('data', (data) => results.push(data))
      .on('end', () => resolve(results))
      .on('error', (error) => reject(new Error(`Error parsing CSV: ${error.message}`)));
  });
}

/**
 * Groups data by year and month
 * @param rows - Array of parsed CSV rows
 * @param selectedColumn - Column to extract values from
 * @returns Record with year-month keys and data for the last day of each month
 */
function groupByMonth(rows: any[], selectedColumn: string): Record<string, any> {
  const monthlyData: Record<string, any> = {};
  
  for (const row of rows) {
    const date = new Date(row.Date);
    const yearMonth = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}`;
    
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
function isLastMonthComplete(latestDate: Date, monthlyData: Record<string, any>): boolean {
  // Check if the latest date is the last day of its month
  const year = latestDate.getFullYear();
  const month = latestDate.getMonth();
  
  // Get the last day of the month
  const lastDayOfMonth = new Date(year, month + 1, 0).getDate();
  
  return latestDate.getDate() === lastDayOfMonth;
}

/**
 * Extracts the last 12 months of data
 * @param monthlyData - Record with year-month keys and data
 * @param lastMonthComplete - Boolean indicating if the last month is complete
 * @returns Array of the last 12 months of data
 */
function extractLastYear(monthlyData: Record<string, any>, lastMonthComplete: boolean): any[] {
  // Get all months in order
  const months = Object.keys(monthlyData).sort();
  
  // If the last month is not complete, remove it
  if (!lastMonthComplete && months.length > 0) {
    months.pop();
  }
  
  // Get the last 12 months (or all if less than 12)
  const lastYearMonths = months.slice(-12);
  
  return lastYearMonths.map(month => ({
    yearMonth: month,
    ...monthlyData[month]
  }));
}

/**
 * Formats the data as required
 * @param lastYear - Array of the last 12 months of data
 * @returns Array of formatted monthly data points
 */
function formatData(lastYear: any[]): MonthlyDataPoint[] {
  const monthNames = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];
  
  return lastYear.map(item => {
    const [year, monthStr] = item.yearMonth.split('-');
    const month = parseInt(monthStr, 10) - 1;
    
    return {
      name: `${monthNames[month]} ${year}`,
      value: item.value
    };
  });
}

// Example usage and test
async function testFunction() {
  try {
    const result = await getLastYearMonthlyData('./data.csv', 'risk_averse');
    console.log(JSON.stringify(result, null, 2));
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Uncomment to run the test
// testFunction();