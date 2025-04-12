import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { AlertCircle, BarChart2, TrendingUp, Activity } from 'lucide-react';
import { fetchMonthlyFinancialDataWithFallback } from '../utils/apiService';

// Type definitions
type RiskLevel = 'risk_averse' | 'moderate' | 'risk_loving';
type InvestmentLength = '3months' | '6months' | '9months' | '1year';
type MarketRegime = 'bull' | 'bear';

interface RevenueData {
  name: string;
  value: number;
}

interface ProductData {
  name: string;
  value: number;
}

interface ChannelData {
  name: string;
  users: number;
  revenue: number;
}

interface TimeSeriesData {
  date: string;
  users: number;
  engagement: number;
}

interface PortfolioChart {
  title: string;
  data: ProductData[];
  description: string;
  tooltipLabel?: string;
  unit?: string;
  colors?: string[];
}

interface SummaryMetrics {
  totalReturn: string;
  portfolioValue: string;
  dividendYield: string;
  riskScore: string;
  changePercent: string;
  riskProfile: string;
}

interface DashboardData {
  revenueData: RevenueData[];
  productData: ProductData[];
  channelData: ChannelData[];
  timeSeriesData: TimeSeriesData[];
  portfolioCharts: PortfolioChart[];
  summaryMetrics: SummaryMetrics;
}

// Color interface
interface ColorScheme {
  primary: string;
  secondary: string;
  tertiary: string;
  quaternary: string;
  success: string;
  warning: string;
  info: string;
  error: string;
  [key: string]: string; // Index signature to allow array-like access
}

const Dashboard: React.FC = () => {
  // User preference states
  const [riskLevel, setRiskLevel] = useState<RiskLevel>('moderate');
  const [investmentLength, setInvestmentLength] =
    useState<InvestmentLength>('1year');
  const [marketRegime, setMarketRegime] = useState<MarketRegime>('bull');

  // Dashboard states
  const [activeChart, setActiveChart] = useState<number>(0);
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(
    null
  );

  // Generate dashboard data based on user preferences
  useEffect(() => {
    generateDashboardData(riskLevel, investmentLength, marketRegime);
  }, []);

  const handlePreferencesSubmit = (): void => {
    generateDashboardData(riskLevel, investmentLength, marketRegime);
  };

  // Colors for consistent styling
  const colors: ColorScheme = {
    primary: '#3f51b5',
    secondary: '#f50057',
    tertiary: '#00bcd4',
    quaternary: '#ff9800',
    success: '#4caf50',
    warning: '#ff9800',
    info: '#2196f3',
    error: '#f44336',
  };

  // Generate data based on user inputs
  const generateDashboardData = async (
    risk: RiskLevel,
    length: InvestmentLength,
    market: MarketRegime
  ): Promise<void> => {
    // Base data to be modified based on inputs
    let revenueData: RevenueData[] = [];
    let productData: ProductData[] = [];
    let channelData: ChannelData[] = [];
    let timeSeriesData: TimeSeriesData[] = [];
    let portfolioCharts: PortfolioChart[] = [];
    let summaryMetrics: SummaryMetrics = {
      totalReturn: '',
      portfolioValue: '',
      dividendYield: '',
      riskScore: '',
      changePercent: '',
      riskProfile: '',
    };

    // Fetch monthly financial data from the API (with fallback)
  const apiResponse = await fetchMonthlyFinancialDataWithFallback(risk);
  
  // Use the API data for revenue/returns
  revenueData = apiResponse.data;

    // Generate revenue/returns data based on inputs
    switch (risk) {
      case 'risk_averse':
        // Lower returns, lower volatility
        // revenueData = [
        //   { name: 'Jan', value: 1.1 },
        //   { name: 'Feb', value: 0.8 },
        //   { name: 'Mar', value: -0.3 },
        //   { name: 'Apr', value: 1.5 },
        //   { name: 'May', value: 1.0 },
        //   { name: 'Jun', value: 1.8 },
        //   { name: 'Jul', value: 1.6 },
        //   { name: 'Aug', value: 1.0 },
        //   { name: 'Sep', value: 0.7 },
        //   { name: 'Oct', value: 1.5 },
        //   { name: 'Nov', value: 1.0 },
        //   { name: 'Dec', value: 1.9 },
        // ];

        productData = [
          { name: 'Treasury Bonds', value: 40 },
          { name: 'Blue Chip Stocks', value: 25 },
          { name: 'Municipal Bonds', value: 20 },
          { name: 'REITs', value: 10 },
          { name: 'Gold', value: 5 },
        ];

        summaryMetrics = {
          totalReturn: '+11.2%',
          portfolioValue: '$1,124,600',
          dividendYield: '2.8%',
          riskScore: '35/100',
          changePercent: '+1.6%',
          riskProfile: 'Conservative',
        };
        break;

      case 'moderate':
        // Moderate returns, moderate volatility
        // revenueData = [
        //   { name: 'Jan', value: 2.5 },
        //   { name: 'Feb', value: 1.8 },
        //   { name: 'Mar', value: -0.7 },
        //   { name: 'Apr', value: 3.2 },
        //   { name: 'May', value: 2.1 },
        //   { name: 'Jun', value: 4.5 },
        //   { name: 'Jul', value: 3.9 },
        //   { name: 'Aug', value: 2.2 },
        //   { name: 'Sep', value: 1.5 },
        //   { name: 'Oct', value: 3.8 },
        //   { name: 'Nov', value: 2.1 },
        //   { name: 'Dec', value: 4.6 },
        // ];

        productData = [
          { name: 'S&P 500 ETF', value: 35 },
          { name: 'International Stocks', value: 25 },
          { name: 'Corporate Bonds', value: 15 },
          { name: 'REITs', value: 15 },
          { name: 'Gold', value: 10 },
        ];

        summaryMetrics = {
          totalReturn: '+24.8%',
          portfolioValue: '$1,350,780',
          dividendYield: '3.4%',
          riskScore: '65/100',
          changePercent: '+3.2%',
          riskProfile: 'Moderate',
        };
        break;

      case 'risk_loving':
        // Higher returns, higher volatility
        // revenueData = [
        //   { name: 'Jan', value: 4.2 },
        //   { name: 'Feb', value: -2.5 },
        //   { name: 'Mar', value: -3.1 },
        //   { name: 'Apr', value: 7.8 },
        //   { name: 'May', value: 5.2 },
        //   { name: 'Jun', value: 6.7 },
        //   { name: 'Jul', value: 8.3 },
        //   { name: 'Aug', value: -2.1 },
        //   { name: 'Sep', value: 3.6 },
        //   { name: 'Oct', value: 6.5 },
        //   { name: 'Nov', value: 4.9 },
        //   { name: 'Dec', value: 7.2 },
        // ];

        productData = [
          { name: 'Growth Stocks', value: 45 },
          { name: 'Emerging Markets', value: 20 },
          { name: 'Cryptocurrencies', value: 15 },
          { name: 'Small-Cap Stocks', value: 15 },
          { name: 'High-Yield Bonds', value: 5 },
        ];

        summaryMetrics = {
          totalReturn: '+38.5%',
          portfolioValue: '$1,782,400',
          dividendYield: '1.8%',
          riskScore: '85/100',
          changePercent: '+5.8%',
          riskProfile: 'Aggressive',
        };
        break;
      default:
        // Default to moderate
        revenueData = [
          { name: 'Jan', value: 2.5 },
          { name: 'Feb', value: 1.8 },
          { name: 'Mar', value: -0.7 },
          { name: 'Apr', value: 3.2 },
          { name: 'May', value: 2.1 },
          { name: 'Jun', value: 4.5 },
          { name: 'Jul', value: 3.9 },
          { name: 'Aug', value: 2.2 },
          { name: 'Sep', value: 1.5 },
          { name: 'Oct', value: 3.8 },
          { name: 'Nov', value: 2.1 },
          { name: 'Dec', value: 4.6 },
        ];
    }

    // Modify data based on market regime
    if (market === 'bear') {
      // Reduce returns in bear market
      revenueData = revenueData.map((month) => ({
        ...month,
        value: month.value * 0.5, // Half the returns in bear market
      }));

      summaryMetrics = {
        ...summaryMetrics,
        totalReturn:
          '+' +
          (
            parseFloat(
              summaryMetrics.totalReturn.replace('%', '').replace('+', '')
            ) * 0.5
          ).toFixed(1) +
          '%',
        portfolioValue:
          '$' +
          (
            parseFloat(
              summaryMetrics.portfolioValue.replace('$', '').replace(/,/g, '')
            ) * 0.85
          ).toLocaleString(),
        changePercent:
          '+' +
          (
            parseFloat(
              summaryMetrics.changePercent.replace('%', '').replace('+', '')
            ) * 0.4
          ).toFixed(1) +
          '%',
      };

      // In bear market, shift asset allocation to more defensive positions
      if (risk === 'risk_averse') {
        productData = [
          { name: 'Treasury Bonds', value: 55 },
          { name: 'Blue Chip Stocks', value: 15 },
          { name: 'Municipal Bonds', value: 20 },
          { name: 'Cash', value: 8 },
          { name: 'Gold', value: 2 },
        ];
      } else if (risk === 'moderate') {
        productData = [
          { name: 'S&P 500 ETF', value: 25 },
          { name: 'Treasury Bonds', value: 30 },
          { name: 'Corporate Bonds', value: 20 },
          { name: 'Cash', value: 15 },
          { name: 'Gold', value: 10 },
        ];
      } else {
        productData = [
          { name: 'Growth Stocks', value: 30 },
          { name: 'Treasury Bonds', value: 20 },
          { name: 'Cryptocurrencies', value: 10 },
          { name: 'Cash', value: 20 },
          { name: 'Gold', value: 20 },
        ];
      }
    }

    // Adjust data based on investment length
    // For shorter timeframes, we'll show fewer data points
    let truncatedRevenueData = [...revenueData];

    if (length === '3months') {
      truncatedRevenueData = revenueData.slice(0, 3);
      timeSeriesData = [
        { date: 'Week 1', users: 2500, engagement: 75 },
        { date: 'Week 2', users: 2700, engagement: 78 },
        { date: 'Week 3', users: 3000, engagement: 82 },
      ];
    } else if (length === '6months') {
      truncatedRevenueData = revenueData.slice(0, 6);
      timeSeriesData = [
        { date: 'Week 1', users: 2500, engagement: 75 },
        { date: 'Week 2', users: 2700, engagement: 78 },
        { date: 'Week 3', users: 3000, engagement: 82 },
        { date: 'Week 4', users: 3200, engagement: 85 },
        { date: 'Week 5', users: 3500, engagement: 88 },
        { date: 'Week 6', users: 3800, engagement: 91 },
      ];
    } else if (length === '9months') {
      truncatedRevenueData = revenueData.slice(0, 9);
      timeSeriesData = [
        { date: 'Week 1', users: 2500, engagement: 75 },
        { date: 'Week 2', users: 2700, engagement: 78 },
        { date: 'Week 3', users: 3000, engagement: 82 },
        { date: 'Week 4', users: 3200, engagement: 85 },
        { date: 'Week 5', users: 3500, engagement: 88 },
        { date: 'Week 6', users: 3800, engagement: 91 },
        { date: 'Week 7', users: 4000, engagement: 93 },
        { date: 'Week 8', users: 4200, engagement: 95 },
        { date: 'Week 9', users: 4400, engagement: 97 },
      ];
    } else {
      // 1 year - use full data
      timeSeriesData = [
        { date: 'Week 1', users: 2500, engagement: 75 },
        { date: 'Week 2', users: 2700, engagement: 78 },
        { date: 'Week 3', users: 3000, engagement: 82 },
        { date: 'Week 4', users: 3200, engagement: 85 },
        { date: 'Week 5', users: 3500, engagement: 88 },
        { date: 'Week 6', users: 3800, engagement: 91 },
        { date: 'Week 7', users: 4000, engagement: 93 },
        { date: 'Week 8', users: 4200, engagement: 95 },
        { date: 'Week 9', users: 4400, engagement: 97 },
        { date: 'Week 10', users: 4600, engagement: 98 },
        { date: 'Week 11', users: 4700, engagement: 98 },
        { date: 'Week 12', users: 4800, engagement: 99 },
      ];
    }

    // Generate asset class data based on risk profile
    if (risk === 'risk_averse') {
      channelData = [
        { name: 'Bonds', users: 5500, revenue: 88000 },
        { name: 'Stocks', users: 2800, revenue: 45000 },
        { name: 'REITs', users: 1200, revenue: 22000 },
        { name: 'Gold', users: 800, revenue: 12000 },
        { name: 'Cash', users: 1800, revenue: 18000 },
      ];
    } else if (risk === 'moderate') {
      channelData = [
        { name: 'Bonds', users: 3800, revenue: 65000 },
        { name: 'Stocks', users: 4500, revenue: 78000 },
        { name: 'REITs', users: 2200, revenue: 42000 },
        { name: 'Gold', users: 1200, revenue: 28000 },
        { name: 'Cash', users: 1500, revenue: 15000 },
      ];
    } else {
      channelData = [
        { name: 'Bonds', users: 1200, revenue: 28000 },
        { name: 'Stocks', users: 5500, revenue: 95000 },
        { name: 'Crypto', users: 2800, revenue: 68000 },
        { name: 'Gold', users: 1500, revenue: 32000 },
        { name: 'Cash', users: 800, revenue: 8000 },
      ];
    }

    // Generate portfolio strategy charts based on risk level
    if (risk === 'risk_averse') {
      portfolioCharts = [
        {
          title: 'Conservative Strategy',
          data: [
            { name: 'Treasury Bonds', value: 40 },
            { name: 'Blue Chip Stocks', value: 30 },
            { name: 'Municipal Bonds', value: 15 },
            { name: 'REITs', value: 10 },
            { name: 'Gold', value: 5 },
          ],
          description:
            'Low-risk strategy focused on capital preservation and stable income',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Income-Focused',
          data: [
            { name: 'Dividend Stocks', value: 40 },
            { name: 'Corporate Bonds', value: 30 },
            { name: 'Preferred Shares', value: 15 },
            { name: 'REITs', value: 15 },
          ],
          colors: ['#4caf50', '#8bc34a', '#ffeb3b', '#f44336'],
          description:
            'Strategy optimized for generating regular passive income',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Inflation Protection',
          data: [
            { name: 'TIPS', value: 40 },
            { name: 'Gold', value: 20 },
            { name: 'Commodities', value: 15 },
            { name: 'Value Stocks', value: 15 },
            { name: 'Real Estate', value: 10 },
          ],
          colors: ['#ff7043', '#f57c00', '#ffa726', '#ffb74d', '#ffe0b2'],
          description: 'Portfolio designed to protect against inflation',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
      ];
    } else if (risk === 'moderate') {
      portfolioCharts = [
        {
          title: 'Balanced Growth',
          data: [
            { name: 'S&P 500 ETF', value: 35 },
            { name: 'International Stocks', value: 25 },
            { name: 'Corporate Bonds', value: 15 },
            { name: 'REITs', value: 15 },
            { name: 'Gold', value: 10 },
          ],
          description: 'Balanced approach with focus on long-term growth',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Income-Growth Hybrid',
          data: [
            { name: 'Dividend Stocks', value: 40 },
            { name: 'Growth Stocks', value: 25 },
            { name: 'Corporate Bonds', value: 20 },
            { name: 'REITs', value: 15 },
          ],
          colors: ['#4caf50', '#8bc34a', '#ffeb3b', '#f44336'],
          description:
            'Strategy balancing growth potential with income generation',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Global Diversification',
          data: [
            { name: 'US Stocks', value: 30 },
            { name: 'International Dev', value: 25 },
            { name: 'Emerging Markets', value: 15 },
            { name: 'Global Bonds', value: 20 },
            { name: 'Alternatives', value: 10 },
          ],
          colors: ['#ff7043', '#f57c00', '#ffa726', '#ffb74d', '#ffe0b2'],
          description: 'Portfolio with global diversification across markets',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
      ];
    } else {
      portfolioCharts = [
        {
          title: 'Aggressive Growth',
          data: [
            { name: 'Growth Stocks', value: 50 },
            { name: 'Emerging Markets', value: 25 },
            { name: 'Cryptocurrencies', value: 15 },
            { name: 'High-Yield Bonds', value: 10 },
          ],
          description:
            'High-risk strategy targeting maximum capital appreciation',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Tech-Focused',
          data: [
            { name: 'Tech Giants', value: 35 },
            { name: 'Cloud Computing', value: 25 },
            { name: 'Semiconductors', value: 20 },
            { name: 'AI & Robotics', value: 20 },
          ],
          colors: ['#4caf50', '#8bc34a', '#ffeb3b', '#f44336'],
          description:
            'Concentrated portfolio focused on technology sector growth',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
        {
          title: 'Thematic Investing',
          data: [
            { name: 'Disruptive Tech', value: 30 },
            { name: 'Clean Energy', value: 25 },
            { name: 'Blockchain', value: 20 },
            { name: 'Space Exploration', value: 15 },
            { name: 'Biotech', value: 10 },
          ],
          colors: ['#ff7043', '#f57c00', '#ffa726', '#ffb74d', '#ffe0b2'],
          description: 'Portfolio targeting innovative, high-growth themes',
          tooltipLabel: 'Allocation',
          unit: '%',
        },
      ];
    }

    setDashboardData({
      revenueData: truncatedRevenueData,
      productData,
      channelData,
      timeSeriesData,
      portfolioCharts,
      summaryMetrics,
    });
  };

  // If data isn't loaded yet, show loading state
  if (!dashboardData) {
    return (
      <div className="flex items-center justify-center h-screen">
        Loading dashboard data...
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-gray-50 p-6">
      <header className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Portfolio Allocation Dashboard
          </h1>
          <p className="text-gray-600">
            Smart asset allocation strategies for optimized investment returns
          </p>
        </div>
      </header>

      {/* User Preference Controls */}
      <div className="mb-6 bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">
          Customize Your Investment Strategy
        </h2>
        <p className="text-gray-600 mb-4">
          Adjust parameters to see personalized recommendations
        </p>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Risk Tolerance
            </label>
            <select
              value={riskLevel}
              onChange={(e) => setRiskLevel(e.target.value as RiskLevel)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="risk_averse">Risk Averse</option>
              <option value="moderate">Moderate</option>
              <option value="risk_loving">Risk Loving</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Investment Timeframe
            </label>
            <select
              value={investmentLength}
              onChange={(e) =>
                setInvestmentLength(e.target.value as InvestmentLength)
              }
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="3months">3 Months</option>
              <option value="6months">6 Months</option>
              <option value="9months">9 Months</option>
              <option value="1year">1 Year</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Market Conditions
            </label>
            <select
              value={marketRegime}
              onChange={(e) => setMarketRegime(e.target.value as MarketRegime)}
              className="w-full p-2 border border-gray-300 rounded-md"
            >
              <option value="bull">Bull Market</option>
              <option value="bear">Bear Market</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Amount Invested ($)
            </label>
            <input
              type="number"
              defaultValue="100000.00"
              min="1000"
              step="1000"
              className="w-full p-2 border border-gray-300 rounded-md"
              placeholder="Enter amount"
              onChange={(e) => {
                // Format to 2 decimal places
                const value = parseFloat(e.target.value);
                if (!isNaN(value)) {
                  e.target.value = value.toFixed(2);
                }
              }}
            />
          </div>
        </div>

        <div className="mt-6 flex justify-center">
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-md"
            onClick={handlePreferencesSubmit}
          >
            Update Recommendations
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-500 mb-2">Total Return</p>
          <div className="text-2xl font-bold text-black">
            {dashboardData.summaryMetrics.totalReturn}
          </div>
          <p className="text-xs text-green-500 flex items-center mt-1">
            <TrendingUp size={14} className="mr-1" />
            {dashboardData.summaryMetrics.changePercent} from previous period
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-500 mb-2">
            Portfolio Value
          </p>
          <div className="text-2xl font-bold text-black">
            {dashboardData.summaryMetrics.portfolioValue}
          </div>
          <p className="text-xs text-green-500 flex items-center mt-1">
            <TrendingUp size={14} className="mr-1" />
            +8.3% from initial investment
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-500 mb-2">
            Dividend Yield
          </p>
          <div className="text-2xl font-bold text-black">
            {dashboardData.summaryMetrics.dividendYield}
          </div>
          <p className="text-xs text-green-500 flex items-center mt-1">
            <TrendingUp size={14} className="mr-1" />
            +0.5% from previous quarter
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm font-medium text-gray-500 mb-2">Risk Score</p>
          <div className="text-2xl font-bold text-black text-black">
            {dashboardData.summaryMetrics.riskScore}
          </div>
          <p className="text-xs text-yellow-500 flex items-center mt-1">
            <TrendingUp size={14} className="mr-1" />
            {dashboardData.summaryMetrics.riskProfile} risk profile
          </p>
        </div>
      </div>

      {/* Performance Chart */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="flex justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">Portfolio Performance</h2>
            <p className="text-gray-600">
              {investmentLength === '3months'
                ? '3 Month'
                : investmentLength === '6months'
                ? '6 Month'
                : investmentLength === '9months'
                ? '9 Month'
                : 'Annual'}{' '}
              returns over time
            </p>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={dashboardData.revenueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                formatter={(value: number) => [
                  `${value.toLocaleString()}%`,
                  'Returns',
                ]}
              />
              <Legend />
              <Area
                type="monotone"
                dataKey="value"
                name="Returns"
                stroke={colors.primary}
                fill={colors.primary}
                fillOpacity={0.2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 text-sm text-gray-500 flex items-center">
          <AlertCircle size={16} className="text-yellow-500 mr-2" />
          <span>
            Portfolio growth of {dashboardData.summaryMetrics.changePercent}{' '}
            compared to previous period
          </span>
        </div>
      </div>

      {/* Recommended Asset Allocation */}
      <div className="mb-6 bg-white p-6 rounded-lg shadow">
        <div className="flex justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">Recommended Asset Allocation</h2>
            <p className="text-gray-600">
              {riskLevel === 'risk_averse'
                ? 'Conservative'
                : riskLevel === 'moderate'
                ? 'Balanced'
                : 'Aggressive'}{' '}
              distribution of investment assets
              {marketRegime === 'bear' ? ' (Bear Market Adjusted)' : ''}
            </p>
          </div>
        </div>

        <div className="h-96 flex justify-center">
          <ResponsiveContainer width="80%" height="100%">
            <PieChart>
              <Pie
                data={dashboardData.productData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }: { name: string; percent: number }) =>
                  `${name}: ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={140}
                fill="#8884d8"
                dataKey="value"
              >
                {dashboardData.productData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={
                      Object.values(colors)[
                        index % Object.values(colors).length
                      ]
                    }
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [`${value}%`, 'Allocation']}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Alternative Strategies Carousel */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold">Alternative Strategies</h2>
          <p className="text-gray-600">
            Explore different portfolio allocation approaches for
            {riskLevel === 'risk_averse'
              ? ' conservative '
              : riskLevel === 'moderate'
              ? ' balanced '
              : ' aggressive '}
            investors
          </p>
        </div>

        <div className="relative">
          {/* Carousel Navigation */}
          <div className="flex justify-between mb-4">
            <button
              className="px-4 py-2 border border-gray-300 rounded-md flex items-center gap-1 text-black"
              onClick={() =>
                setActiveChart(
                  activeChart === 0
                    ? dashboardData.portfolioCharts.length - 1
                    : activeChart - 1
                )
              }
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="m15 18-6-6 6-6" />
              </svg>
              Previous
            </button>
            <div className="flex items-center gap-1">
              {dashboardData.portfolioCharts.map((_, index) => (
                <div
                  key={index}
                  className={`w-2 h-2 rounded-full mx-1 cursor-pointer ${
                    index === activeChart ? 'bg-blue-600' : 'bg-gray-300'
                  }`}
                  onClick={() => setActiveChart(index)}
                />
              ))}
            </div>
            <button
              className="px-4 py-2 border border-gray-300 rounded-md flex items-center gap-1 text-black"
              onClick={() =>
                setActiveChart(
                  (activeChart + 1) % dashboardData.portfolioCharts.length
                )
              }
            >
              Next
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="m9 18 6-6-6-6" />
              </svg>
            </button>
          </div>

          {/* Carousel Content */}
          <div className="flex overflow-hidden">
            {dashboardData.portfolioCharts.map((chart, index) => (
              <div
                key={index}
                className={`w-full transition-transform duration-300 ease-in-out ${
                  index === activeChart
                    ? 'translate-x-0'
                    : index < activeChart
                    ? '-translate-x-full'
                    : 'translate-x-full'
                }`}
                style={{ display: index === activeChart ? 'block' : 'none' }}
              >
                <div className="text-lg font-medium mb-2 text-center">
                  {chart.title}
                </div>
                <div className="h-96 flex justify-center">
                  <ResponsiveContainer width="80%" height="100%">
                    <PieChart>
                      <Pie
                        data={chart.data}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({
                          name,
                          percent,
                        }: {
                          name: string;
                          percent: number;
                        }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        outerRadius={140}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {chart.data.map((entry, i) => (
                          <Cell
                            key={`cell-${i}`}
                            fill={
                              chart.colors
                                ? chart.colors[i % chart.colors.length]
                                : Object.values(colors)[
                                    i % Object.values(colors).length
                                  ]
                            }
                          />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value: number) => [
                          `${value}${chart.unit || '%'}`,
                          chart.tooltipLabel || 'Value',
                        ]}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="text-sm text-gray-500 mt-2 text-center">
                  {chart.description}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Asset Class Performance */}
      <div className="bg-white p-6 rounded-lg shadow mb-6">
        <div className="mb-4">
          <h2 className="text-xl font-bold">Asset Class Performance</h2>
          <p className="text-gray-600">Performance metrics by asset class</p>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dashboardData.channelData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis
                yAxisId="left"
                orientation="left"
                stroke={colors.primary}
              />
              <YAxis
                yAxisId="right"
                orientation="right"
                stroke={colors.secondary}
              />
              <Tooltip />
              <Legend />
              <Bar
                yAxisId="left"
                dataKey="users"
                name="Allocation"
                fill={colors.primary}
                radius={[4, 4, 0, 0]}
              />
              <Bar
                yAxisId="right"
                dataKey="revenue"
                name="Returns ($)"
                fill={colors.secondary}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <footer className="bg-white p-4 rounded-lg shadow text-center text-gray-500 text-sm">
        <p>
          Portfolio recommendations are based on your risk profile, investment
          timeframe, and current market conditions
        </p>
        <p className="mt-2">Data last updated: March 31, 2025</p>
      </footer>
    </div>
  );
};

export default Dashboard;
