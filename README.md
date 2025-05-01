# AI-Driven Stock Sentiment Analysis & Recommendation System

A full-stack web application designed to assist investors and financial analysts by analyzing stock-related sentiment from real-time data sources and generating actionable investment recommendations.

## Architecture Overview

- **Data Collection Layer**: Web scrapers and APIs to gather financial data
- **Processing Layer**: Sentiment analysis using AI models like VADER
- **Backend Service Layer**: Handles user requests and processes data
- **Recommendation Engine**: Analyzes sentiment trends to suggest investment opportunities
- **Notification & UI Layer**: Interactive dashboards with alerts

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL

### Backend Setup

1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - MacOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables in `.env`
6. Set up MySQL database:
   - Create a database named `stock_sentiment`
   - Update database credentials in `.env`
   - Run the following SQL commands to reset tables and update schema:
     ```sql
     DELETE FROM sentiment_data;
     DELETE FROM recommendations;
     DELETE FROM notifications;

     ALTER TABLE sentiment_data ADD COLUMN stock_symbol VARCHAR(20);
     ```
7. Run migrations: `python manage.py migrate`
8. Run the server: `python app.py`

### Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Start the development server: `npm start`
4. If any error comes regarding version of node js please run this command on terminal - export NODE\_OPTIONS=--openssl-legacy-provider.



## Features

- Sentiment analysis on stock data
- Real-time alerts
- Stock trend visualization
- Investment recommendations
