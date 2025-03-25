# Amazon Product Review Sentiment Analyzer

A full-stack application that analyzes Amazon product reviews using Natural Language Processing to provide sentiment analysis and insights.

## Features
- Real-time Amazon review scraping
- Sentiment analysis using VADER
- Interactive data visualization dashboard
- Aspect-based sentiment analysis
- Trend analysis over time

## Setup Instructions

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
```

3. Start the backend server:
```bash
uvicorn backend.main:app --reload
```

4. Start the frontend development server:
```bash
cd frontend
npm start
```

## Project Structure
- `/backend`: FastAPI server and analysis logic
- `/frontend`: React frontend application
- `/data`: Cached data and analysis results
