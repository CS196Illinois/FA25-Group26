import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';

const api = axios.create ({
baseURL: API_BASE_URL,
headers: {
    'Content-Type': 'application/json',
},
});


// ============ HEALTH CHECK ============
export const checkHealth = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

// ============ STOCK DATA & PREDICTION ============
export const getStockPrediction = async (ticker) => {
  const response = await api.post('/api/stock/predict', { ticker });
  return response.data;
};

// ============ DETAILED FORECAST ============
export const getDetailedForecast = async (ticker, horizon = 20, lags = 10) => {
  const response = await api.post('/api/stock/forecast', {
    ticker,
    horizon,
    lags
  });
  return response.data;
};

// ============ NEWS SENTIMENT ============
export const getNewsSentiment = async (ticker, keyword = null) => {
  const response = await api.post('/api/news/sentiment', {
    ticker,
    keyword: keyword || ticker
  });
  return response.data;
};

// ============ PORTFOLIO ============
export const getPortfolioData = async (tickers) => {
  const response = await api.post('/api/portfolio', { tickers });
  return response.data;
};

export default api;