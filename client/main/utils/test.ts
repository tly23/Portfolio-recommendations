import { getLastYearMonthlyData } from './monthly-data-extractor';

async function main() {
  try {
    const result = await getLastYearMonthlyData('../../../output/line_chart_data.csv', 'risk_averse');
    console.log(result);
  } catch (error) {
    console.error('Error:', error);
  }
}

main();