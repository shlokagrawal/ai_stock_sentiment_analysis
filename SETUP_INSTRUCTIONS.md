# Setup Instructions for Stock Sentiment Analysis System

This guide will help you set up and run the AI-Driven Stock Sentiment Analysis & Recommendation System.

## Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL

## Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the environment variables:
   - Create a `.env` file in the backend directory
   - Add the following variables:
     ```
     FLASK_APP=app.py
     FLASK_ENV=development
     FLASK_DEBUG=1
     
     DB_USER=root
     DB_PASSWORD=your_mysql_password
     DB_HOST=localhost
     DB_NAME=stock_sentiment
     
     SECRET_KEY=your_secret_key_for_jwt
     ```

6. Set up the MySQL database:
   - Create a new database named `stock_sentiment`
   - Update the database credentials in your `.env` file
   - Note: The application uses PyMySQL for database connections, so you don't need MySQL client libraries installed

7. Initialize the database with sample data:
   ```
   python init_db.py
   ```

8. Start the backend server:
   ```
   python app.py
   ```
   The server will run on http://localhost:5000

## Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```
   The frontend will run on http://localhost:3000

## Sample Users

The system is initialized with these sample users:

1. Admin User
   - Email: admin@example.com
   - Password: admin123

2. Analyst User
   - Email: analyst@example.com
   - Password: analyst123

3. Regular User
   - Email: user@example.com
   - Password: user123

## Features

- User authentication (login, register, profile management)
- Stock listing and details
- Sentiment analysis of stock-related news
- Investment recommendations based on sentiment analysis
- User watchlist for tracking stocks
- Notifications for important stock events

## API Documentation

The backend API is organized into the following endpoints:

- Authentication: `/api/auth/`
- Stocks: `/api/stocks/`
- Sentiment Analysis: `/api/sentiment/`
- Recommendations: `/api/recommendations/`

For detailed API documentation, see the README.md file in each module.

## Troubleshooting

If you encounter any issues:

1. Make sure you have all the required dependencies installed
2. Check that your MySQL server is running
3. Verify your database credentials in the `.env` file
4. Check the application logs for specific error messages

For further assistance, please create an issue in the project repository. 