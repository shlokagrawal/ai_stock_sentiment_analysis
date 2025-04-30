// src/pages/StockDetails.js

import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
  Button,
  Chip,
  Divider,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import { 
  getStockBySymbol, 
  refreshStockData, 
  getStockSentiment, 
  getAggregateSentiment,
  refreshSentiment,
  getStockRecommendation,
  loadSentimentData,
  loadRecommendationData
} from '../services/apiService';

const StockDetails = () => {
  const { stockId } = useParams();
  const [loading, setLoading] = useState(true);
  const [stock, setStock] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  
  // State for sentiment analysis
  const [sentimentData, setSentimentData] = useState([]);
  const [aggregateSentiment, setAggregateSentiment] = useState(null);
  const [sentimentLoading, setSentimentLoading] = useState(false);
  const [sentimentError, setSentimentError] = useState('');
  
  // State for recommendations
  const [recommendation, setRecommendation] = useState(null);
  const [recommendationLoading, setRecommendationLoading] = useState(false);
  const [recommendationError, setRecommendationError] = useState('');
  
  useEffect(() => {
    const loadStockData = async () => {
      setLoading(true);
      try {
        const result = await getStockBySymbol(stockId);
        if (result.success) {
          setStock(result.stock);
        } else {
          setError('Failed to load stock data');
        }
      } catch (err) {
        console.error('Error loading stock:', err);
        setError('An error occurred while loading stock data');
      } finally {
        setLoading(false);
      }
    };
    
    loadStockData();
  }, [stockId]);
  
  // Load sentiment data when switching to sentiment tab
  useEffect(() => {
    if (activeTab === 1 && stock && stock.symbol) {
      loadSentimentData(stock.symbol);
    }
    
  }, [activeTab, stockId]);
  
  // Load recommendation data when switching to recommendations tab
  useEffect(() => {
    if (activeTab === 2 && stockId) {
      loadRecommendationData();
    }
  }, [activeTab, stockId]);
  
  const loadSentimentData = async (symbol) => {
    setSentimentLoading(true);
    setSentimentError('');
  
    try {
      const [sentimentResult, aggregateResult] = await Promise.all([
        getStockSentiment(symbol),
        getAggregateSentiment(symbol)
      ]);
  
      if (sentimentResult.success) {
        setSentimentData(sentimentResult.sentimentData || []);
      } else if (sentimentResult.error?.includes("No sentiment data")) {
        console.warn("No sentiment found, refreshing...");
        await refreshSentiment(symbol);
        setTimeout(() => loadSentimentData(symbol), 3000); // retry after 3s
        return;
      }
  
      if (aggregateResult.success) {
        setAggregateSentiment(aggregateResult.aggregatedSentiment);
      } else if (aggregateResult.error?.includes("No sentiment data")) {
        console.warn("No aggregate sentiment found, refreshing...");
        await refreshSentiment(symbol);
        setTimeout(() => loadSentimentData(symbol), 3000); // retry after 3s
      }
    } catch (err) {
      console.error('Error loading sentiment data:', err);
      setSentimentError('An error occurred while loading sentiment data');
    } finally {
      setSentimentLoading(false);
    }
  };
  
  
  const loadRecommendationData = async () => {
    setRecommendationLoading(true);
    setRecommendationError('');
    
    try {
      const result = await getStockRecommendation(stock.symbol);
      
      if (result.success) {
        setRecommendation(result.recommendation);
      } else {
        setRecommendationError('Failed to load recommendation data');
      }
    } catch (err) {
      console.error('Error loading recommendation data:', err);
      setRecommendationError('An error occurred while loading recommendation data');
    } finally {
      setRecommendationLoading(false);
    }
  };
  
  const handleRefreshSentiment = async () => {
    setSentimentLoading(true);
    
    try {
      const result = await refreshSentiment(stock.symbol);

      
      if (result.success) {
        // Reload sentiment data after refresh
        await loadSentimentData();
      } else {
        setSentimentError('Failed to refresh sentiment data');
      }
    } catch (err) {
      console.error('Error refreshing sentiment:', err);
      setSentimentError('An error occurred while refreshing sentiment data');
    } finally {
      setSentimentLoading(false);
    }
  };
  
  const handleRefreshStockData = async () => {
    setLoading(true);
    
    try {
      const result = await refreshStockData(stockId);
      
      if (result.success) {
        setStock(result.stock);
      } else {
        setError('Failed to refresh stock data');
      }
    } catch (err) {
      console.error('Error refreshing stock:', err);
      setError('An error occurred while refreshing stock data');
    } finally {
      setLoading(false);
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
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error" sx={{ mt: 3 }}>
          {error}
        </Alert>
      ) : stock ? (
        <Box>
          <Box sx={{ mb: 4 }}>
            <Typography variant="h4" component="h1" gutterBottom>
              {stock.name} ({stock.symbol})
            </Typography>
            <Typography variant="h5" color="primary">
              ${stock.current_price?.toFixed(2)}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Sector: {stock.sector || 'N/A'}
            </Typography>
          </Box>
          
          <Box sx={{ width: '100%', mb: 4 }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
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
              <Box sx={{ py: 3 }}>
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
                            Previous Close: ${stock.previous_close?.toFixed(2)}
                          </Typography>
                        </Box>
                        
                        <Button 
                          variant="contained" 
                          color="primary" 
                          sx={{ mt: 2 }}
                          onClick={handleRefreshStockData}
                        >
                          Refresh Data
                        </Button>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>
              </Box>
            )}
            
            {activeTab === 1 && (
              <Box sx={{ py: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Sentiment Analysis
                </Typography>
                
                {sentimentLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : sentimentError ? (
                  <Alert severity="error" sx={{ mt: 3 }}>
                    {sentimentError}
                  </Alert>
                ) : (
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
                              No sentiment data available.
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
                          
                          <Button 
                            variant="contained" 
                            color="primary" 
                            sx={{ mb: 2 }}
                            onClick={handleRefreshSentiment}
                          >
                            Refresh Sentiment Data
                          </Button>
                          
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
                              No recent news articles found.
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>
                  </Grid>
                )}
              </Box>
            )}
            
            {activeTab === 2 && (
              <Box sx={{ py: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Investment Recommendations
                </Typography>
                
                {recommendationLoading ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                  </Box>
                ) : recommendationError ? (
                  <Alert severity="error" sx={{ mt: 3 }}>
                    {recommendationError}
                  </Alert>
                ) : recommendation ? (
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
                    No recommendation data available for this stock.
                  </Typography>
                )}
              </Box>
            )}
          </Box>
        </Box>
      ) : (
        <Alert severity="info" sx={{ mt: 3 }}>
          Stock not found
        </Alert>
      )}
    </Container>
  );
};

export default StockDetails; 