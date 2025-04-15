// apiService.ts

// Define the risk level type to ensure we only use valid values
export type RiskLevel = 'risk_averse' | 'risk_loving' | 'moderate';

// Type definition for the monthly data returned by the API
export interface MonthlyDataPoint {
  name: string; // e.g., "Jan 2023"
  value: number; // e.g., 1.5 (representing 1.5% return)
}

// Type definition for the API response
export interface MonthlyDataResponse {
  data: MonthlyDataPoint[];
}

/**
 * Fetches monthly financial data based on risk level
 * 
 * @param riskLevel - The desired risk level strategy
 * @param baseUrl - Optional base URL for the API (defaults to localhost:8000)
 * @returns Promise containing the monthly financial data
 */
export const fetchMonthlyFinancialData = async (
  riskLevel: RiskLevel,
  baseUrl: string = 'http://localhost:8000'
): Promise<MonthlyDataResponse> => {
  try {
    // Construct the API URL with the risk level parameter
    const url = `${baseUrl}/api/monthly-data/?risk_level=${riskLevel}`;
    
    // Make the API request
    const response = await fetch(url);
    
    // Check if the request was successful
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed with status ${response.status}: ${errorText}`);
    }
    
    // Parse the JSON response
    const data: MonthlyDataResponse = await response.json();
    
    // Validate the response structure
    if (!data || !Array.isArray(data.data)) {
      throw new Error('Invalid API response format');
    }
    
    return data;
  } catch (error) {
    // Log the error for debugging
    console.error('Error fetching monthly financial data:', error);
    
    // Re-throw the error so it can be handled by the caller
    throw error;
  }
};

/**
 * Fetches monthly financial data with automatic error handling and fallback data
 * 
 * @param riskLevel - The desired risk level strategy
 * @param fallbackData - Optional fallback data to use if the API request fails
 * @returns Promise containing the monthly financial data or fallback data
 */
export const fetchMonthlyFinancialDataWithFallback = async (
  riskLevel: RiskLevel,
  fallbackData?: MonthlyDataResponse
): Promise<MonthlyDataResponse> => {
  try {
    // Attempt to fetch data from the API
    return await fetchMonthlyFinancialData(riskLevel);
  } catch (error) {
    console.warn('Using fallback data due to API error:', error);
    
    // If fallback data was provided, return it
    if (fallbackData) {
      return fallbackData;
    }
    
    // Default fallback data based on risk level
    const defaultFallbackData: Record<RiskLevel, MonthlyDataResponse> = {
      'risk_averse': {
        data: [
          { name: 'Jan', value: 1.1 },
          { name: 'Feb', value: 0.8 },
          { name: 'Mar', value: -0.3 },
          { name: 'Apr', value: 1.5 },
          { name: 'May', value: 1.0 },
          { name: 'Jun', value: 1.8 },
          { name: 'Jul', value: 1.6 },
          { name: 'Aug', value: 1.0 },
          { name: 'Sep', value: 0.7 },
          { name: 'Oct', value: 1.5 },
          { name: 'Nov', value: 1.0 },
          { name: 'Dec', value: 1.9 },
        ]
      },
      'moderate': {
        data: [
          { name: 'Jan', value: 1.8 },
          { name: 'Feb', value: 1.2 },
          { name: 'Mar', value: -0.5 },
          { name: 'Apr', value: 2.4 },
          { name: 'May', value: 1.9 },
          { name: 'Jun', value: 2.7 },
          { name: 'Jul', value: 2.3 },
          { name: 'Aug', value: 1.5 },
          { name: 'Sep', value: 0.9 },
          { name: 'Oct', value: 2.3 },
          { name: 'Nov', value: 1.8 },
          { name: 'Dec', value: 2.8 },
        ]
      },
      'risk_loving': {
        data: [
          { name: 'Jan', value: 2.4 },
          { name: 'Feb', value: 1.9 },
          { name: 'Mar', value: -1.2 },
          { name: 'Apr', value: 3.8 },
          { name: 'May', value: 2.9 },
          { name: 'Jun', value: 3.9 },
          { name: 'Jul', value: 3.4 },
          { name: 'Aug', value: 2.3 },
          { name: 'Sep', value: 1.2 },
          { name: 'Oct', value: 3.6 },
          { name: 'Nov', value: 2.7 },
          { name: 'Dec', value: 4.1 },
        ]
      }
    };
    
    console.log('Using default fallback data:', defaultFallbackData[riskLevel]);
    return defaultFallbackData[riskLevel];
  }
};