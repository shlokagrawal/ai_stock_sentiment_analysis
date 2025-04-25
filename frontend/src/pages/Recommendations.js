import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  CircularProgress,
  Alert,
  Divider,
  Chip,
} from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import ShowChartIcon from '@mui/icons-material/ShowChart';
import { getTopRecommendations } from '../services/apiService';

const Recommendations = () => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState([]);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const loadRecommendations = async () => {
      setLoading(true);
      try {
        const result = await getTopRecommendations(10); // Get top 10 recommendations
        if (result.success) {
          setRecommendations(result.topRecommendations);
        } else {
          setError('Failed to load recommendations');
        }
      } catch (err) {
        console.error('Error loading recommendations:', err);
        setError('An error occurred while loading recommendations');
      } finally {
        setLoading(false);
      }
    };
    
    loadRecommendations();
  }, []);
  
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
  
  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Investment Recommendations
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Here are our AI-driven investment recommendations based on sentiment analysis.
        </Typography>
      </Box>
      
      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      ) : recommendations && recommendations.length > 0 ? (
        <Grid container spacing={3}>
          {recommendations.map((item) => (
            <Grid item xs={12} md={6} lg={4} key={item.stock.id}>
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
                    View Details
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      ) : (
        <Alert severity="info">
          No recommendations available at this time.
        </Alert>
      )}
    </Container>
  );
};

export default Recommendations; 