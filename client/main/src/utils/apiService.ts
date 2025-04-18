// apiService.ts

// Define the risk level type to ensure we only use valid values
export type RiskLevel = 'risk_averse' | 'risk_loving' | 'moderate' | '60_40' | 'SPY';

// Type definition for the monthly data returned by the API
export interface MonthlyDataPoint {
  name: string; // e.g., "Jan 2023"
  value: number; // e.g., 1.5 (representing 1.5% return)
  SPY: number;
  _60_40: number;
}

// Type definition for the API response
export interface MonthlyDataResponse {
  data: MonthlyDataPoint[];
}

export interface AssetDataPoint {
  name: string;
  value: number;
}

export interface AssetDataResponse {
  data: AssetDataPoint[];
}

/**
 * Fetches monthly financial data based on risk level
 * 
 * @param riskLevel - The desired risk level strategy
 * @param baseUrl - Optional base URL for the API (defaults to localhost:8000)
 * @returns Promise containing the monthly financial data
 */

export const fetchAssetAllocationData = async (
  riskLevel: RiskLevel,
  baseUrl: string = 'http://localhost:8000'
): Promise<AssetDataResponse> => {
  try {
    // Construct the API URL with the risk level parameter
    if  (riskLevel === 'SPY' || riskLevel === '60_40') {
      let alternateData: Partial<Record<RiskLevel, AssetDataResponse>> = {
        '60_40': {
        data: [
          { name: 'SPY', value: 60.0 },  
          { name: 'TLT', value: 40.0 }
        ]},
      'SPY': {
        data: [
          { name: 'Technology Stocks', value: 31.00 },
          { name: 'Financial Services', value: 14.21 },
          { name: 'Healthcare', value: 11.19 },
          { name: 'Consumer Cyclical', value: 10.35 },
          { name: 'Communication Services', value: 9.33 },
          { name: 'Industrials', value: 7.46 },
          { name: 'Consumer Defensive', value: 6.03 },
          { name: 'Energy', value: 3.66 },
          { name: 'Utilities', value: 2.72 },
          { name: 'Real Estate', value: 2.27 },
          { name: 'Basic Materials', value: 1.79 }
        ]}
      }

      return alternateData[riskLevel] as AssetDataResponse;
    }
    const url = `${baseUrl}/api/asset_allocation/?risk_level=${riskLevel}`;
    
    // Make the API request
    const response = await fetch(url);
    
    // Check if the request was successful
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API request failed with status ${response.status}: ${errorText}`);
    }
    
    // Parse the JSON response
    const data: AssetDataResponse = await response.json();
    
    // Validate the response structure
    if (!data || !Array.isArray(data.data)) {
      throw new Error('Invalid API response format');
    }

    return data;
  } catch (error) {
    // Log the error for debugging
    console.error('Error fetching monthly financial data:', error);
    
    
//     Asset Class,weights
// MAG7,7.91
// Bonds,0.17
// Commodities,1.24
// Crypto,0.0
// Market_Indices,3.94
// Low_Beta_Stocks,15.13
// High_Beta_Growth_Stocks,24.18
// Other_Stocks,47.43


    const defaultFallbackData: Partial<Record<RiskLevel, AssetDataResponse>> = {
      'risk_averse': {
        data: [
          { name: 'MAG7', value: 7.91 },
          { name: 'Bonds', value: 0.17 },
          { name: 'Commodities', value: 1.24 },
          { name: 'Crypto', value: 0.0 },
          { name: 'Market_Indices', value: 3.94},
          { name: 'Low_Beta_Stocks', value: 15.13 },
          { name: 'High_Beta_Growth_Stocks', value: 24.18 },
          { name: 'Other_Stocks', value: 47.43}
        ]
      },
      'moderate': {
        data: [
          { name: 'MAG7', value: 7.91 },
          { name: 'Bonds', value: 0.17 },
          { name: 'Commodities', value: 1.24 },
          { name: 'Crypto', value: 0.0 },
          { name: 'Market_Indices', value: 3.94},
          { name: 'Low_Beta_Stocks', value: 15.13 },
          { name: 'High_Beta_Growth_Stocks', value: 24.18 },
          { name: 'Other_Stocks', value: 47.43}
        ]
      },
      'risk_loving': {
        data: [
          { name: 'MAG7', value: 7.91 },
          { name: 'Bonds', value: 0.17 },
          { name: 'Commodities', value: 1.24 },
          { name: 'Crypto', value: 0.0 },
          { name: 'Market_Indices', value: 3.94},
          { name: 'Low_Beta_Stocks', value: 15.13 },
          { name: 'High_Beta_Growth_Stocks', value: 24.18 },
          { name: 'Other_Stocks', value: 47.43}
        ]},
      
    };
    
    console.log('Using default fallback data:', defaultFallbackData[riskLevel]);
    return defaultFallbackData[riskLevel] as AssetDataResponse;
    // Re-throw the error so it can be handled by the caller
    //throw error;
  }
};


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

    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    // , SPY: 1, _60_40: 2 
    
    // Default fallback data based on risk level
    const defaultFallbackData: Record<RiskLevel, MonthlyDataResponse> = {
      'risk_averse': {
        data: [
          { name: 'Jan', value: 1.1  , SPY: 1, _60_40: 2 },
          { name: 'Feb', value: 0.8  , SPY: 1, _60_40: 2 },
          { name: 'Mar', value: -0.3 , SPY: 1, _60_40: 2 },
          { name: 'Apr', value: 1.5  , SPY: 1, _60_40: 2 },
          { name: 'May', value: 1.0  , SPY: 1, _60_40: 2 },
          { name: 'Jun', value: 1.8  , SPY: 1, _60_40: 2 },
          { name: 'Jul', value: 1.6  , SPY: 1, _60_40: 2 },
          { name: 'Aug', value: 1.0  , SPY: 1, _60_40: 2 },
          { name: 'Sep', value: 0.7  , SPY: 1, _60_40: 2 },
          { name: 'Oct', value: 1.5  , SPY: 1, _60_40: 2 },
          { name: 'Nov', value: 1.0  , SPY: 1, _60_40: 2 },
          { name: 'Dec', value: 1.9  , SPY: 1, _60_40: 2 },
        ]
      },
      'moderate': {
        data: [
          { name: 'Jan', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Feb', value: 1.2 , SPY: 1, _60_40: 2 },
          { name: 'Mar', value: -0.5, SPY: 1, _60_40: 2 },
          { name: 'Apr', value: 2.4 , SPY: 1, _60_40: 2 },
          { name: 'May', value: 1.9 , SPY: 1, _60_40: 2 },
          { name: 'Jun', value: 2.7 , SPY: 1, _60_40: 2 },
          { name: 'Jul', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Aug', value: 1.5 , SPY: 1, _60_40: 2 },
          { name: 'Sep', value: 0.9 , SPY: 1, _60_40: 2 },
          { name: 'Oct', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Nov', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Dec', value: 2.8 , SPY: 1, _60_40: 2 },
        ]
      },
      'risk_loving': {
        data: [
          { name: 'Jan', value: 2.4 , SPY: 1, _60_40: 2 },
          { name: 'Feb', value: 1.9 , SPY: 1, _60_40: 2 },
          { name: 'Mar', value: -1.2, SPY: 1, _60_40: 2  },
          { name: 'Apr', value: 3.8 , SPY: 1, _60_40: 2 },
          { name: 'May', value: 2.9 , SPY: 1, _60_40: 2 },
          { name: 'Jun', value: 3.9 , SPY: 1, _60_40: 2 },
          { name: 'Jul', value: 3.4 , SPY: 1, _60_40: 2 },
          { name: 'Aug', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Sep', value: 1.2 , SPY: 1, _60_40: 2 },
          { name: 'Oct', value: 3.6 , SPY: 1, _60_40: 2 },
          { name: 'Nov', value: 2.7 , SPY: 1, _60_40: 2 },
          { name: 'Dec', value: 4.1 , SPY: 1, _60_40: 2 },
        ]
      },
      '60_40': {
        data: [
          { name: 'Jan', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Feb', value: 1.2 , SPY: 1, _60_40: 2 },
          { name: 'Mar', value: -0.5, SPY: 1, _60_40: 2  },
          { name: 'Apr', value: 2.4 , SPY: 1, _60_40: 2 },
          { name: 'May', value: 1.9 , SPY: 1, _60_40: 2 },
          { name: 'Jun', value: 2.7 , SPY: 1, _60_40: 2 },
          { name: 'Jul', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Aug', value: 1.5 , SPY: 1, _60_40: 2 },
          { name: 'Sep', value: 0.9 , SPY: 1, _60_40: 2 },
          { name: 'Oct', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Nov', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Dec', value: 2.8 , SPY: 1, _60_40: 2 },
        ]
      },
      'SPY': {  
        data: [
          { name: 'Jan', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Feb', value: 1.2 , SPY: 1, _60_40: 2 },
          { name: 'Mar', value: -0.5, SPY: 1, _60_40: 2  },
          { name: 'Apr', value: 2.4 , SPY: 1, _60_40: 2 },  
          { name: 'May', value: 1.9 , SPY: 1, _60_40: 2 },
          { name: 'Jun', value: 2.7 , SPY: 1, _60_40: 2 },
          { name: 'Jul', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Aug', value: 1.5 , SPY: 1, _60_40: 2 },
          { name: 'Sep', value: 0.9 , SPY: 1, _60_40: 2 },
          { name: 'Oct', value: 2.3 , SPY: 1, _60_40: 2 },
          { name: 'Nov', value: 1.8 , SPY: 1, _60_40: 2 },
          { name: 'Dec', value: 2.8 , SPY: 1, _60_40: 2 },
        ]
      }
    };
    
    console.log('Using default fallback data:', defaultFallbackData[riskLevel]);
    return defaultFallbackData[riskLevel];
  }
};