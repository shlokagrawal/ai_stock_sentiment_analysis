//from frontend/src/pages/LiveAnalysis.js

import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  TextField,
  Button,
  CircularProgress,
  Alert,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
  Paper,
  Tabs,
  Tab
} from '@mui/material';
import { 
  searchLiveStock, 
  getStockSentiment, 
  getAggregateSentiment,
  getStockRecommendation,
  getLiveStockDetails,
  getLiveStockHistory,  
  getRefreshSentiment,
  refreshSentiment,
  loadSentimentData
} from '../services/apiService';

const LiveAnalysis = () => {
  const [symbol, setSymbol] = useState('');
  const [loading, setLoading] = useState(false);
  const [stock, setStock] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [dataSource, setDataSource] = useState('');
  const [loadingDetails, setLoadingDetails] = useState(false);
  const [stockDetails, setStockDetails] = useState(null);
  const [historicalData, setHistoricalData] = useState([]);
  
  // State for sentiment and recommendation
  const [sentimentData, setSentimentData] = useState([]);
  const [aggregateSentiment, setAggregateSentiment] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!symbol) return;
    
    setLoading(true);
    setError('');
    setStock(null);
    setSentimentData([]);
    setAggregateSentiment(null);
    setRecommendation(null);
    setStockDetails(null);
    setHistoricalData([]);
    
    try {
      // Search for the stock by symbol using Yahoo Finance
      const result = await searchLiveStock(symbol);
      console.log('Search result:', result); // For debugging
      
      if (result.success && result.stock) {
        setStock(result.stock);
        setDataSource(result.source || 'unknown');
        
        // If this is a new stock from Yahoo Finance
        if (result.source === 'yahoo_finance' || result.source === 'yahoo_finance_only') {
         
          await refreshSentiment(result.stock.symbol); // <-- This triggers scraping
          await new Promise((resolve) => setTimeout(resolve, 3000)); // wait 3s
          await loadSentimentData(result.stock.symbol); // <-- Now reload data
        } else {
          await Promise.all([
            loadSentimentData(result.stock.symbol),
            loadRecommendationData(result.stock.symbol)
          ]);
        }
        
        
        // Load additional stock details and history
        if (result.stock.symbol) {
          await Promise.all([
            loadStockDetails(result.stock.symbol),
            loadStockHistory(result.stock.symbol)
          ]);
        }
      } else {
        setError(result.error || 'Stock not found. Please check the symbol and try again.');
      }
    } catch (err) {
      console.error('Error in live analysis:', err);
      setError('An error occurred while analyzing the stock. Please try again later.');
    } finally {
      setLoading(false);
    }
  };
  
  let retryCount = 0;

  const loadSentimentData = async (symbol) => {
    try {
      const [sentimentResult, aggregateResult] = await Promise.all([
        getStockSentiment(symbol),
        getAggregateSentiment(symbol)
      ]);
  
      if (sentimentResult.success) {
        setSentimentData(sentimentResult.sentimentData || []);
      } else if (retryCount < 1 && sentimentResult.error?.includes("No sentiment data")) {
        await refreshSentiment(symbol);
        retryCount++;
        setTimeout(() => loadSentimentData(symbol), 3000);
        return;
      }
  
      if (aggregateResult.success) {
        setAggregateSentiment(aggregateResult.aggregatedSentiment);
      }
    } catch (err) {
      console.error('Error loading sentiment data:', err);
    }
  };
  
  
  const loadRecommendationData = async (symbol) => {
    try {
      const result = await getStockRecommendation(symbol); // ✅ pass symbol here
      if (result.success) {
        setRecommendation(result.recommendation);
      }
    } catch (err) {
      console.error('Error loading recommendation data:', err);
    }
  };
  
  
  const loadStockDetails = async (symbol) => {
    setLoadingDetails(true);
    try {
      const result = await getLiveStockDetails(symbol);
      if (result.success) {
        setStockDetails(result.stock);
      }
    } catch (err) {
      console.error('Error loading stock details:', err);
    } finally {
      setLoadingDetails(false);
    }
  };
  
  const loadStockHistory = async (symbol) => {
    try {
      const result = await getLiveStockHistory(symbol, '1mo');
      if (result.success) {
        setHistoricalData(result.history || []);
      }
    } catch (err) {
      console.error('Error loading stock history:', err);
    }
  };
  
  const handleChangeTab = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const getSentimentColor = (sentiment) => {
    if (!sentiment) return 'default';
    
    if (sentiment === 'positive') return 'success';
    if (sentiment === 'negative') return 'error';
    return 'default'; // neutral
  };
  
  const getRecommendationColor = (type) => {
    if (!type) return 'default';
    
    if (type === 'buy') return 'success';
    if (type === 'sell') return 'error';
    return 'warning'; // hold
  };
  
  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Live Stock Analysis with Yahoo Finance
        </Typography>
        <Typography variant="body1" gutterBottom>
          Enter any stock symbol to get real-time analysis and recommendations
        </Typography>
        
        <Paper sx={{ p: 3, mt: 3 }}>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={8}>
                <TextField
                  fullWidth
                  label="Stock Symbol"
                  variant="outlined"
                  placeholder="e.g., AAPL, MSFT, GOOG"
                  value={symbol}
                  onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                  required
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <Button 
                  fullWidth
                  type="submit"
                  variant="contained" 
                  color="primary"
                  disabled={loading}
                >
                  {loading ? 'Analyzing...' : 'Analyze Stock'}
                </Button>
              </Grid>
            </Grid>
          </form>
        </Paper>
      </Box>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 6 }}>
          <CircularProgress />
        </Box>
      ) : error && !stock ? (
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      ) : stock ? (
        <Box>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h5" component="h2" gutterBottom>
              {stock.name} ({stock.symbol})
            </Typography>
            <Typography variant="h6" color="primary">
              ${stock.current_price?.toFixed(2)}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Sector: {stock.sector || 'N/A'}
            </Typography>
            {dataSource && (
              <Chip 
                label={`Source: ${dataSource}`} 
                size="small" 
                sx={{ mt: 1 }} 
                color={dataSource === 'cache' ? 'secondary' : 'primary'} 
              />
            )}
          </Box>
          
          {error && (
            <Alert severity="info" sx={{ mb: 3 }}>
              {error}
            </Alert>
          )}
          
          <Box sx={{ width: '100%', mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
              <Tabs 
                value={activeTab} 
                onChange={handleChangeTab}
              >
                <Tab label="Overview" />
                <Tab label="Sentiment Analysis" />
                <Tab label="Recommendations" />
              </Tabs>
            </Box>
            
            {activeTab === 0 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Stock Overview
                </Typography>
                <Grid container spacing={3}>
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Price Information
                        </Typography>
                        <Box sx={{ my: 2 }}>
                          <Typography variant="body1">
                            Current Price: ${stock.current_price?.toFixed(2)}
                          </Typography>
                          <Typography variant="body1">
                            Previous Close: ${stock.previous_close?.toFixed(2) || 'N/A'}
                          </Typography>
                          <Typography variant="body1">
                            Market Cap: ${(stock.market_cap / 1000000000).toFixed(2) || 'N/A'} B
                          </Typography>
                          <Typography variant="body1">
                            Volume: {stock.volume?.toLocaleString() || 'N/A'}
                          </Typography>
                        </Box>
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  {stockDetails && (
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Company Details
                          </Typography>
                          <Box sx={{ my: 2 }}>
                            <Typography variant="body1">
                              Industry: {stockDetails.industry || 'N/A'}
                            </Typography>
                            <Typography variant="body1">
                              Country: {stockDetails.country || 'N/A'}
                            </Typography>
                            <Typography variant="body1">
                              P/E Ratio: {stockDetails.pe_ratio?.toFixed(2) || 'N/A'}
                            </Typography>
                            <Typography variant="body1">
                              Dividend Yield: {stockDetails.dividend_yield ? `${(stockDetails.dividend_yield * 100).toFixed(2)}%` : 'N/A'}
                            </Typography>
                            {stockDetails.website && (
                              <Typography variant="body1">
                                Website: <a href={stockDetails.website} target="_blank" rel="noopener noreferrer">{stockDetails.website}</a>
                              </Typography>
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                  
                  {historicalData.length > 0 && (
                    <Grid item xs={12}>
                      <Card>
                        <CardContent>
                          <Typography variant="h6" gutterBottom>
                            Recent Performance (Last {historicalData.length} Days)
                          </Typography>
                          <Box sx={{ mt: 2, maxHeight: 300, overflow: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                              <thead style={{ position: 'sticky', top: 0, background: '#fff' }}>
                                <tr>
                                  <th style={{ padding: '8px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>Date</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>Open</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>High</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>Low</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>Close</th>
                                  <th style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>Volume</th>
                                </tr>
                              </thead>
                              <tbody>
                                {historicalData.map((day, index) => (
                                  <tr key={day.date}>
                                    <td style={{ padding: '8px', textAlign: 'left', borderBottom: '1px solid #ddd' }}>{day.date}</td>
                                    <td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>${day.open.toFixed(2)}</td>
                                    <td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>${day.high.toFixed(2)}</td>
                                    <td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>${day.low.toFixed(2)}</td>
                                    <td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>${day.close.toFixed(2)}</td>
                                    <td style={{ padding: '8px', textAlign: 'right', borderBottom: '1px solid #ddd' }}>{day.volume.toLocaleString()}</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>
                  )}
                </Grid>
              </Box>
            )}
            
            {activeTab === 1 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Sentiment Analysis
                </Typography>
                
                <Grid container spacing={3}>
                  {/* Aggregate Sentiment Card */}
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Overall Sentiment
                        </Typography>
                        
                        {aggregateSentiment ? (
                          <Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                              <Typography variant="body1" sx={{ mr: 1 }}>
                                Market Sentiment:
                              </Typography>
                              <Chip 
                                label={aggregateSentiment.sentiment_label?.toUpperCase() || 'NEUTRAL'} 
                                color={getSentimentColor(aggregateSentiment.sentiment_label)}
                                size="small"
                              />
                            </Box>
                            
                            <Box sx={{ mb: 2 }}>
                              <Typography variant="body2">
                                Compound Score: {aggregateSentiment.compound_score?.toFixed(2) || 'N/A'}
                              </Typography>
                              <Typography variant="body2">
                                Positive: {(aggregateSentiment.positive_score * 100)?.toFixed(0)}%
                              </Typography>
                              <Typography variant="body2">
                                Neutral: {(aggregateSentiment.neutral_score * 100)?.toFixed(0)}%
                              </Typography>
                              <Typography variant="body2">
                                Negative: {(aggregateSentiment.negative_score * 100)?.toFixed(0)}%
                              </Typography>
                            </Box>
                          </Box>
                        ) : (
                          <Typography variant="body1">
                            No sentiment data available. Please check back later as our system analyzes recent news related to this stock.
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                  
                  {/* Recent News Sentiment */}
                  <Grid item xs={12} md={6}>
                    <Card>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          Recent News Sentiment
                        </Typography>
                        
                        {sentimentData.length > 0 ? (
                          <List>
                            {sentimentData.slice(0, 5).map((item, index) => (
                              <React.Fragment key={item.id || index}>
                                <ListItem alignItems="flex-start">
                                  <ListItemText
                                    primary={
                                      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                                        <Typography variant="body1" component="span">
                                          {item.title || 'News Article'}
                                        </Typography>
                                        <Chip 
                                          label={item.sentiment_label?.toUpperCase() || 'NEUTRAL'} 
                                          color={getSentimentColor(item.sentiment_label)}
                                          size="small"
                                        />
                                      </Box>
                                    }
                                    secondary={
                                      <>
                                        <Typography variant="body2" component="span">
                                          Source: {item.source || 'Unknown'}
                                        </Typography>
                                        {item.url && (
                                          <Typography variant="body2" component="div">
                                            <a href={item.url} target="_blank" rel="noopener noreferrer">
                                              Read more
                                            </a>
                                          </Typography>
                                        )}
                                      </>
                                    }
                                  />
                                </ListItem>
                                {index < sentimentData.slice(0, 5).length - 1 && <Divider />}
                              </React.Fragment>
                            ))}
                          </List>
                        ) : (
                          <Typography variant="body1">
                            No recent news articles found for this stock. Please check back later.
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {activeTab === 2 && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  Investment Recommendations
                </Typography>
                
                {recommendation ? (
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                            <Typography variant="h6" sx={{ mr: 2 }}>
                              Recommendation:
                            </Typography>
                            <Chip 
                              label={recommendation.type?.toUpperCase() || 'HOLD'} 
                              color={getRecommendationColor(recommendation.type)}
                              size="medium"
                            />
                          </Box>
                          
                          <Box sx={{ mb: 2 }}>
                            <Typography variant="body1" gutterBottom>
                              <strong>Confidence Score:</strong> {(recommendation.confidence_score * 100)?.toFixed(0)}%
                            </Typography>
                            
                            {recommendation.price_target && (
                              <Typography variant="body1" gutterBottom>
                                <strong>Price Target:</strong> ${recommendation.price_target?.toFixed(2)}
                              </Typography>
                            )}
                            
                            <Typography variant="body1" gutterBottom>
                              <strong>Time Frame:</strong> {recommendation.time_frame || 'Short-term'}
                            </Typography>
                            
                            <Typography variant="body1" sx={{ mt: 2 }}>
                              <strong>Analysis:</strong>
                            </Typography>
                            <Typography variant="body1" paragraph>
                              {recommendation.reason || 'No detailed analysis available.'}
                            </Typography>
                          </Box>
                          
                          <Typography variant="body2" color="text.secondary">
                            Last updated: {new Date(recommendation.created_at).toLocaleString()}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                ) : (
                  <Typography variant="body1">
                    No recommendation data available for this stock. Please check back later as our system generates recommendations.
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        </Box>
      ) : null}
    </Container>
  );
};

export default LiveAnalysis; 