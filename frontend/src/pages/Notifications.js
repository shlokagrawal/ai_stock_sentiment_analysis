import React, { useState, useEffect } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemButton,
  Divider,
  IconButton,
  CircularProgress,
  Alert,
  Paper,
  Button,
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import NewReleasesIcon from '@mui/icons-material/NewReleases';
import DeleteIcon from '@mui/icons-material/Delete';
import { formatDistanceToNow } from 'date-fns';

// This would come from an API in a real implementation
const mockNotifications = [
  {
    id: 1,
    title: 'Price Alert: AAPL',
    message: 'AAPL has moved significantly. Current price: $175.50',
    type: 'alert',
    is_read: false,
    reference_id: 1,
    reference_type: 'stock',
    created_at: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 minutes ago
  },
  {
    id: 2,
    title: 'New Recommendation: MSFT',
    message: 'We have a new buy recommendation for MSFT',
    type: 'recommendation',
    is_read: true,
    reference_id: 2,
    reference_type: 'stock',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
  },
  {
    id: 3,
    title: 'News Alert: TSLA',
    message: 'New important news about Tesla, Inc. that might affect its price',
    type: 'news',
    is_read: false,
    reference_id: 5,
    reference_type: 'stock',
    created_at: new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(), // 5 hours ago
  },
];

const Notifications = () => {
  const [loading, setLoading] = useState(true);
  const [notifications, setNotifications] = useState([]);
  const [error, setError] = useState('');
  
  useEffect(() => {
    // Simulate API call
    setLoading(true);
    setTimeout(() => {
      setNotifications(mockNotifications);
      setLoading(false);
    }, 1000);
  }, []);
  
  const handleMarkAsRead = (notificationId) => {
    setNotifications(notifications.map(notification => 
      notification.id === notificationId 
        ? { ...notification, is_read: true }
        : notification
    ));
  };
  
  const handleDelete = (notificationId) => {
    setNotifications(notifications.filter(notification => 
      notification.id !== notificationId
    ));
  };
  
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'alert':
        return <NotificationsActiveIcon color="warning" />;
      case 'recommendation':
        return <TrendingUpIcon color="primary" />;
      case 'news':
        return <NewReleasesIcon color="info" />;
      default:
        return <NotificationsIcon />;
    }
  };
  
  return (
    <Container>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Notifications
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Stay updated on important stock events and recommendations.
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
      ) : notifications.length > 0 ? (
        <Paper elevation={2}>
          <List>
            {notifications.map((notification, index) => (
              <React.Fragment key={notification.id}>
                {index > 0 && <Divider />}
                <ListItem
                  secondaryAction={
                    <IconButton 
                      edge="end" 
                      aria-label="delete"
                      onClick={() => handleDelete(notification.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  }
                  disablePadding
                  sx={{
                    bgcolor: notification.is_read ? 'inherit' : 'action.hover',
                  }}
                >
                  <ListItemButton 
                    component={RouterLink}
                    to={`/stocks/${notification.reference_id}`}
                    onClick={() => handleMarkAsRead(notification.id)}
                  >
                    <ListItemIcon>
                      {getNotificationIcon(notification.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={notification.title}
                      secondary={
                        <React.Fragment>
                          <Typography
                            sx={{ display: 'block' }}
                            component="span"
                            variant="body2"
                            color="text.primary"
                          >
                            {notification.message}
                          </Typography>
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                        </React.Fragment>
                      }
                    />
                  </ListItemButton>
                </ListItem>
              </React.Fragment>
            ))}
          </List>
        </Paper>
      ) : (
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <NotificationsIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary" gutterBottom>
            No notifications
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            You don't have any notifications at this time.
          </Typography>
          <Button 
            variant="contained" 
            component={RouterLink} 
            to="/"
          >
            Go to Dashboard
          </Button>
        </Box>
      )}
    </Container>
  );
};

export default Notifications; 