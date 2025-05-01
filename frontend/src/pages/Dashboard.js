//src/pages/Dashboard.js

import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Grid,
  Typography,
  Card,
  CardContent,
  CardActions,
  Button,
  Box,
  Chip,
  Divider,
  Paper,
  CircularProgress,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import { useAuth } from '../context/AuthContext';
import {
  getWatchlist,
  addToWatchlist,
  removeFromWatchlist,
} from '../services/apiService';
import { getTopRecommendations } from '../services/apiService';

const Dashboard = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [topStocks, setTopStocks] = useState([]);
  const [watchlist, setWatchlist] = useState([]);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Get top recommendations
        const recResult = await getTopRecommendations();
        if (recResult.success) {
          setTopStocks(recResult.topRecommendations);
        }
        
        // Get user's watchlist
        const watchlistResult = await getWatchlist();
        if (watchlistResult.success) {
          setWatchlist(watchlistResult.watchlist);
        }
      } catch (err) {
        console.error('Error loading dashboard data:', err);
        setError('Failed to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, []);
  
  const handleAddToWatchlist = async (stockId) => {
    try {
      const result = await addToWatchlist(stockId);
      if (result.success) {
        // Refresh watchlist
        const watchlistResult = await getWatchlist();
        if (watchlistResult.success) {
          setWatchlist(watchlistResult.watchlist);
        }
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Error adding to watchlist:', err);
      setError('Failed to add stock to watchlist.');
    }
  };
  
  const handleRemoveFromWatchlist = async (stockId) => {
    try {
      const result = await removeFromWatchlist(stockId);
      if (result.success) {
        // Update watchlist by filtering out the removed stock
        setWatchlist((prev) => prev.filter((stock) => stock.id !== stockId));
      } else {
        setError(result.error);
      }
    } catch (err) {
      console.error('Error removing from watchlist:', err);
      setError('Failed to remove stock from watchlist.');
    }
  };
  
  const getRecommendationIcon = (type) => {
    switch (type) {
      case 'buy':
        return <TrendingUpIcon sx={{ color: 'success.main' }} />;
      case 'sell':
        return <TrendingDownIcon sx={{ color: 'error.main' }} />;
      default:
        return <TrendingFlatIcon sx={{ color: 'warning.main' }} />;
    }
  };
  
  const handleChangeTab = (event, newValue) => {
    setActiveTab(newValue);
  };
  
  const isStockInWatchlist = (stockId) => {
    return watchlist.some((stock) => stock.id === stockId);
  };

  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome back, {user?.username || 'User'}! Here's your stock market overview.
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      
      <Paper sx={{ mb: 4 }}>
        <Tabs 
          value={activeTab} 
          onChange={handleChangeTab}
          variant="fullWidth"
        >
          <Tab label="Top Recommendations" />
          <Tab label="Your Watchlist" />
        </Tabs>
      </Paper>
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : (
        <Box>
          {activeTab === 0 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Top Stock Recommendations
              </Typography>
              
              {topStocks.length === 0 ? (
                <Alert severity="info">
                  No recommendations available at this time. Try refreshing later.
                </Alert>
              ) : (
                <Grid container spacing={3}>
                  {topStocks.map((item) => (
                    <Grid item xs={12} sm={6} md={4} key={item.stock.id}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h6">
                              {item.stock.symbol}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              ${item.stock.current_price?.toFixed(2)}
                            </Typography>
                          </Box>
                          
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {item.stock.name}
                          </Typography>
                          
                          <Divider sx={{ my: 1 }} />
                          
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                            {getRecommendationIcon(item.recommendation.type)}
                            <Chip 
                              label={item.recommendation.type.toUpperCase()} 
                              color={
                                item.recommendation.type === 'buy' 
                                  ? 'success' 
                                  : item.recommendation.type === 'sell' 
                                    ? 'error' 
                                    : 'warning'
                              }
                              size="small"
                              sx={{ ml: 1 }}
                            />
                            <Box sx={{ flexGrow: 1 }} />
                            <Typography variant="body2">
                              {Math.round(item.recommendation.confidence_score * 100)}% confidence
                            </Typography>
                          </Box>
                          
                          <Typography variant="body2" gutterBottom>
                            {item.recommendation.reason}
                          </Typography>
                        </CardContent>
                        <CardActions>
                          <Button 
                            size="small" 
                            component={RouterLink} 
                            to={`/stocks/${item.stock.id}`}
                            startIcon={<ShowChartIcon />}
                          >
                            Details
                          </Button>
                          {isStockInWatchlist(item.stock.id) ? (
                            <Button 
                              size="small" 
                              color="error" 
                              onClick={() => handleRemoveFromWatchlist(item.stock.id)}
                            >
                              Remove from Watchlist
                            </Button>
                          ) : (
                            <Button 
                              size="small" 
                              startIcon={<AddIcon />}
                              onClick={() => handleAddToWatchlist(item.stock.id)}
                            >
                              Add to Watchlist
                            </Button>
                          )}
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          )}
          
          {activeTab === 1 && (
            <Box>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Your Watchlist
              </Typography>
              
              {watchlist.length === 0 ? (
                <Alert severity="info">
                  Your watchlist is empty. Add stocks to your watchlist to track them here.
                </Alert>
              ) : (
                <Grid container spacing={3}>
                  {watchlist.map((stock) => (
                    <Grid item xs={12} sm={6} md={4} key={stock.id}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                            <Typography variant="h6">
                              {stock.symbol}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              ${stock.current_price?.toFixed(2)}
                            </Typography>
                          </Box>
                          
                          <Typography variant="body2" color="text.secondary" gutterBottom>
                            {stock.name}
                          </Typography>
                          
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="body2">
                              Sector: {stock.sector || 'N/A'}
                            </Typography>
                            {stock.previous_close && (
                              <Typography variant="body2">
                                Previous Close: ${stock.previous_close.toFixed(2)}
                              </Typography>
                            )}
                          </Box>
                        </CardContent>
                        <CardActions>
                          <Button 
                            size="small" 
                            component={RouterLink} 
                            to={`/stocks/${stock.id}`}
                            startIcon={<ShowChartIcon />}
                          >
                            Details
                          </Button>
                          <Button 
                            size="small" 
                            color="error" 
                            onClick={() => handleRemoveFromWatchlist(stock.id)}
                          >
                            Remove
                          </Button>
                        </CardActions>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}
            </Box>
          )}
        </Box>
      )}
    </Container>
  );
};

export default Dashboard; 