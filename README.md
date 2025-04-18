# Portfolio Analysis Application

## Overview
A comprehensive financial portfolio analysis application with Python backend for data processing and React frontend for visualization. This application provides data-driven insights through clustering, optimization, and detailed analytics.

## Table of Contents
- [Architecture](#architecture)
- [Features](#features)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation and Setup](#installation-and-setup)
- [Development](#development)
- [API Documentation](#api-documentation)
- [Data Flow](#data-flow)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Architecture
```
┌─────────────────┐       ┌────────────────┐       ┌─────────────────┐
│                 │       │                │       │                 │
│  React Frontend │◄─────►│  Python API    │◄─────►│     Database    │
│                 │       │                │       │                 │
└─────────────────┘       └────────────────┘       └─────────────────┘
```

## Features
- Asset class allocation analysis
- Portfolio optimization algorithms
- Data cleaning and preprocessing
- Clustering analysis for market insights
- Interactive visualizations
- Heatmap generation
- Historical equity curve analysis

## Technologies

### Frontend
- React
- Chart visualization libraries
- Tailwind CSS
- Vite for build tooling

### Backend
- Python
- Data analysis libraries (Pandas, NumPy, SciPy)
- Machine learning frameworks
- RESTful API structure


## Project Structure
```
/
├── .github/                        # GitHub specific files including workflows
├── big_data/                       # Storage for large datasets
├── charts/                         # Generated visualization outputs
│   ├── asset_class_allocation_charts/
│   ├── cleaning_charts/
│   ├── clustering_charts/
│   ├── equity_cuve_charts/
│   ├── feature_creation_charts/
│   ├── optimization_charts/
│   ├── portfolio_results_charts/
│   └── portfolio_weights/
├── client/                         # Frontend React application
│   ├── heatmap/                    # Heatmap specific components
│   └── main/                       # Main React application
│       ├── public/                 # Static assets
│       ├── src/                    # Source code
│       │   ├── assets/             # Media files and static resources
│       │   ├── components/         # Reusable UI components
│       │   └── utils/              # Frontend utilities
│       └── ... (build files)
├── output/                         # Output files from data processing
├── pdfs/                           # PDF reports and documentation
├── portfolio_weights/              # Portfolio weight calculations
└── __pycache__/                    # Python cache files
```

## Prerequisites
- Python 3.8+
- Node.js 16+
- Required Python packages: pandas, numpy, scipy, sklearn, etc.
- NPM or Yarn

## Installation and Setup

### Clone the repository
```bash
# Make a folder to house the virtual environment 
mkdir python_env

git clone https://github.com/tly23/Portfolio-recommendations.git

```

### Backend Setup
```bash
# Create virtual environment
python -m venv .

#For Linux and Mac: Activate virtual environment
source bin/activate  

# For Windows: Activate virtual environment
Scripts\activate

# Install Python dependencies
pip install -r Portfolio-recommendations/requirements.txt
```

### Run Data Pipeline
```bash
# Go into the Portfolio-recommendations base directory
cd Portfolio-recommendations

# Run Data pipeline script abd wait for it to complete
# Note: this might take a while.
python setup_script.py
```

### Backend Setup
```bash
# In a different terminal window, in Portfolio-recommendations directory, start the backend server
python backend_server.py
```

### Frontend Setup
```bash
# In a different terminal window, Navigate to the main client directory
cd Portfolio-recommendations/client/main

# Install dependencies
npm install

# Start the development server
npm run dev
```

## Development

### Backend Development
- Data processing pipelines
- Financial analysis algorithms
- Portfolio optimization techniques
- API endpoints for frontend consumption

### Frontend Development
- Interactive charting components
- Dashboard layouts
- Responsive design for various devices
- Data visualization best practices

## API Documentation
Key endpoints for accessing portfolio analysis functionality:

```
GET /api/monthly-data/
GET /api/asset_allocation/
```
## Dasboard Walkthrough
Users choose desired values for:
- Risk Tolerance:
    - Options: ```Risk Averse```, ```Risk Loving```, ```Moderate```
- Investment Timeframe : 
    - Options: ```3 Months```, ```6 Months```, ```9 Months```, ```1 Year```
- Amount Invested

Charts:
- % Returns Line chart
- Portfolio allocation Pie Chart 

## Data Flow
1. Raw financial data is collected in the `big_data` directory
2. Python backend processes and analyzes the data
3. Results are stored in output directory
4. Frontend consumes processed data through API calls
5. Visualizations render in the browser for user interaction


## License
Specify the license used for your project (MIT, Apache 2.0, etc.).
