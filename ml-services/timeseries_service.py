from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict
import uvicorn

app = FastAPI(title="Time-Series Analysis Service")

# Initialize time-series data
print("Loading time-series analysis system...")
try:
    # Create simulated historical misinformation trends database
    def create_historical_database():
        """Create simulated time-series data for misinformation trends"""
        
        # Categories of misinformation
        categories = {
            'vaccine_misinfo': {
                'keywords': ['vaccine', 'vaccination', 'immunization', 'shot', 'jab'],
                'baseline': 0.3,
                'volatility': 0.2
            },
            'health_misinfo': {
                'keywords': ['cure', 'treatment', 'medicine', 'poison', 'toxic', 'deadly'],
                'baseline': 0.25,
                'volatility': 0.15
            },
            'conspiracy': {
                'keywords': ['they', 'control', 'plan', 'secret', 'hiding', 'truth'],
                'baseline': 0.2,
                'volatility': 0.25
            },
            'political_misinfo': {
                'keywords': ['election', 'vote', 'rigged', 'fraud', 'manipulation'],
                'baseline': 0.15,
                'volatility': 0.3
            },
            'social_misinfo': {
                'keywords': ['community', 'group', 'people', 'attack', 'threat'],
                'baseline': 0.1,
                'volatility': 0.2
            }
        }
        
        # Generate 90 days of historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        data = []
        for category, config in categories.items():
            for date in dates:
                # Simulate trend with some randomness
                days_from_start = (date - start_date).days
                trend = config['baseline'] + np.sin(days_from_start / 15) * 0.1
                noise = np.random.normal(0, config['volatility'] * 0.1)
                value = max(0, min(1, trend + noise))
                
                data.append({
                    'date': date,
                    'category': category,
                    'harm_level': value,
                    'volume': int(np.random.exponential(100) * (1 + value))
                })
        
        return pd.DataFrame(data), categories
    
    historical_df, categories_config = create_historical_database()
    print(f"Time-series database initialized with {len(historical_df)} records")
    USE_FALLBACK = False
    
except Exception as e:
    print(f"Error loading time-series system: {e}")
    print("Running in Fallback Mode (Simulated trends)")
    historical_df = None
    categories_config = None
    USE_FALLBACK = True


class TextInput(BaseModel):
    text: str


class TrendData(BaseModel):
    category: str
    current_level: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    volatility: float
    recent_spike: bool


class TimeSeriesAnalysis(BaseModel):
    detected_categories: List[str]
    trends: List[TrendData]
    historical_context: str
    risk_forecast: str
    similar_incidents: List[Dict[str, str]]


def categorize_text(text: str) -> List[str]:
    """Categorize text based on keywords"""
    if USE_FALLBACK or categories_config is None:
        # Simple fallback categorization
        text_lower = text.lower()
        categories = []
        
        if any(w in text_lower for w in ['vaccine', 'vaccination', 'immunization']):
            categories.append('vaccine_misinfo')
        if any(w in text_lower for w in ['cure', 'treatment', 'poison', 'toxic']):
            categories.append('health_misinfo')
        if any(w in text_lower for w in ['they', 'control', 'secret', 'hiding']):
            categories.append('conspiracy')
        if any(w in text_lower for w in ['election', 'vote', 'rigged']):
            categories.append('political_misinfo')
        if any(w in text_lower for w in ['attack', 'threat', 'community']):
            categories.append('social_misinfo')
        
        return categories if categories else ['general']
    
    text_lower = text.lower()
    detected = []
    
    for category, config in categories_config.items():
        if any(keyword in text_lower for keyword in config['keywords']):
            detected.append(category)
    
    return detected if detected else ['general']


def analyze_trend(category: str) -> TrendData:
    """Analyze trend for a specific category"""
    if USE_FALLBACK or historical_df is None:
        # Fallback trend data
        return TrendData(
            category=category,
            current_level=0.5,
            trend_direction="stable",
            volatility=0.2,
            recent_spike=False
        )
    
    # Filter data for category
    category_data = historical_df[historical_df['category'] == category].sort_values('date')
    
    if len(category_data) == 0:
        return TrendData(
            category=category,
            current_level=0.3,
            trend_direction="stable",
            volatility=0.1,
            recent_spike=False
        )
    
    # Get recent data (last 7 days)
    recent_data = category_data.tail(7)
    current_level = recent_data['harm_level'].mean()
    
    # Calculate trend direction
    if len(recent_data) >= 2:
        recent_avg = recent_data.tail(3)['harm_level'].mean()
        older_avg = category_data.tail(14).head(7)['harm_level'].mean()
        
        if recent_avg > older_avg * 1.1:
            trend_direction = "increasing"
        elif recent_avg < older_avg * 0.9:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
    else:
        trend_direction = "stable"
    
    # Calculate volatility
    volatility = recent_data['harm_level'].std()
    
    # Detect recent spike
    recent_spike = recent_data['harm_level'].max() > category_data['harm_level'].quantile(0.9)
    
    return TrendData(
        category=category,
        current_level=round(current_level, 3),
        trend_direction=trend_direction,
        volatility=round(volatility, 3),
        recent_spike=recent_spike
    )


def generate_historical_context(categories: List[str], trends: List[TrendData]) -> str:
    """Generate historical context narrative"""
    if not trends:
        return "No significant historical patterns detected for this type of content."
    
    context_parts = []
    
    for trend in trends:
        if trend.trend_direction == "increasing":
            context_parts.append(
                f"📈 **{trend.category.replace('_', ' ').title()}**: "
                f"Currently trending upward (level: {int(trend.current_level*100)}%). "
                f"This type of misinformation has seen increased activity in recent days."
            )
        elif trend.recent_spike:
            context_parts.append(
                f"⚠️ **{trend.category.replace('_', ' ').title()}**: "
                f"Recent spike detected. Similar claims have shown elevated harm levels recently."
            )
        else:
            context_parts.append(
                f"📊 **{trend.category.replace('_', ' ').title()}**: "
                f"Baseline activity (level: {int(trend.current_level*100)}%). "
                f"Trend is {trend.trend_direction}."
            )
    
    return "\n\n".join(context_parts)


def generate_risk_forecast(trends: List[TrendData]) -> str:
    """Generate risk forecast based on trends"""
    if not trends:
        return "Insufficient data for risk forecasting."
    
    # Calculate overall risk
    increasing_trends = sum(1 for t in trends if t.trend_direction == "increasing")
    recent_spikes = sum(1 for t in trends if t.recent_spike)
    avg_level = np.mean([t.current_level for t in trends])
    
    if recent_spikes > 0 or increasing_trends >= 2:
        forecast = "🔴 **High Risk Period**: Multiple indicators suggest elevated misinformation activity. "
        forecast += "Similar claims are likely to spread rapidly in current environment."
    elif increasing_trends == 1 or avg_level > 0.5:
        forecast = "🟡 **Moderate Risk**: Some upward trends detected. "
        forecast += "Monitor for escalation and verify claims carefully."
    else:
        forecast = "🟢 **Normal Risk Level**: No significant trend anomalies. "
        forecast += "Standard verification practices recommended."
    
    return forecast


def find_similar_incidents(categories: List[str]) -> List[Dict[str, str]]:
    """Find similar historical incidents"""
    incidents = [
        {
            'category': 'vaccine_misinfo',
            'date': '2024-01-15',
            'description': 'Vaccine microchip claims surged, leading to protest organization',
            'outcome': 'Debunked by health authorities, but caused temporary vaccine hesitancy spike'
        },
        {
            'category': 'health_misinfo',
            'date': '2024-02-03',
            'description': 'False cure claims spread rapidly on social media',
            'outcome': 'Led to hospitalizations from unsafe self-medication'
        },
        {
            'category': 'conspiracy',
            'date': '2023-12-20',
            'description': 'Coordinated conspiracy narrative targeting specific groups',
            'outcome': 'Increased online harassment and real-world confrontations'
        },
        {
            'category': 'political_misinfo',
            'date': '2024-01-28',
            'description': 'Election fraud claims without evidence',
            'outcome': 'Undermined trust in democratic processes'
        },
        {
            'category': 'social_misinfo',
            'date': '2024-02-10',
            'description': 'False claims about community poisoning food supplies',
            'outcome': 'Led to boycotts and community tensions'
        }
    ]
    
    # Filter incidents matching detected categories
    relevant = [inc for inc in incidents if inc['category'] in categories]
    
    return relevant[:3]  # Return top 3


@app.post("/analyze", response_model=TimeSeriesAnalysis)
async def analyze_timeseries(input_data: TextInput):
    """Analyze text for time-series trends and historical context"""
    try:
        # Categorize the text
        categories = categorize_text(input_data.text)
        
        # Analyze trends for each category
        trends = [analyze_trend(cat) for cat in categories]
        
        # Generate historical context
        historical_context = generate_historical_context(categories, trends)
        
        # Generate risk forecast
        risk_forecast = generate_risk_forecast(trends)
        
        # Find similar incidents
        similar_incidents = find_similar_incidents(categories)
        
        return TimeSeriesAnalysis(
            detected_categories=categories,
            trends=trends,
            historical_context=historical_context,
            risk_forecast=risk_forecast,
            similar_incidents=similar_incidents
        )
    
    except Exception as e:
        print(f"Error in time-series analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "time-series-analysis",
        "mode": "fallback" if USE_FALLBACK else "full",
        "records": len(historical_df) if historical_df is not None else 0
    }


if __name__ == "__main__":
    print("Starting Time-Series Analysis Service on port 8006...")
    uvicorn.run(app, host="0.0.0.0", port=8006)
