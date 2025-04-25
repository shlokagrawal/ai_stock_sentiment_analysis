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
} from '@mui/material';
import { getStockById, refreshStockData } from '../services/apiService';
import { getStockSentiment, refreshSentiment } from '../services/apiService';
import { getStockRecommendation } from '../services/apiService';

const StockDetails = () => {
  const { stockId } = useParams();
  const [loading, setLoading] = useState(true);
  const [stock, setStock] = useState(null);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  
  useEffect(() => {
    const loadStockData = async () => {
      setLoading(true);
      try {
        const result = await getStockById(stockId);
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
  
  const handleChangeTab = (event, newValue) => {
    setActiveTab(newValue);
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
                          onClick={() => {
                            // Placeholder for refresh function
                            alert('This would refresh the stock data');
                          }}
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
                <Typography variant="body1">
                  Sentiment analysis data will be displayed here.
                </Typography>
              </Box>
            )}
            
            {activeTab === 2 && (
              <Box sx={{ py: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Investment Recommendations
                </Typography>
                <Typography variant="body1">
                  Stock recommendations will be displayed here.
                </Typography>
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