# Modified feedback.py with full async support
from config import AI_BASE_DIR
from imports import *
import pytz

import asyncio
router = APIRouter()
templates = Jinja2Templates(directory="templates")

router = APIRouter()
templates = Jinja2Templates(directory="templates")

MODEL_DIR = os.path.join(AI_BASE_DIR, "sentimentmodel", "checkpoint-1500")
sentiment_analyzer = SentimentAnalyzer(MODEL_DIR)

@router.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("employee/feedback.html", {"request": request})

@router.post("/submit-feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    feedbackType: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle feedback submission asynchronously"""
    # Verify authentication
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Decode token in a separate thread to avoid blocking
    token_data = await asyncio.to_thread(decode_access_token, token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Generate feedback ID
    feedback_id = f"FDB{random.randint(10000, 99999)}"
    
    # Run sentiment analysis asynchronously
    sentiment_result = await sentiment_analyzer.predict(message)
    feedback_summary = f"{sentiment_result['predicted_label']} {sentiment_result['confidence_score']:.2f}%"

    # Get current time and convert to Nepal timezone
    utc_time = datetime.now(pytz.utc)
    nepal_time = await asyncio.to_thread(convert_utc_to_nepal_local, utc_time)

    # Create feedback object
    new_feedback = SupportFeedback(
        feedback_id=feedback_id,
        user_id=user_id,
        feedback_type=feedbackType,
        message=message,
        feedback_summary=feedback_summary,
        created_at=nepal_time,
    )
    
    # Save to database using thread executor to avoid blocking
    await asyncio.to_thread(lambda: (db.add(new_feedback), db.commit()))

    # Return success response
    return templates.TemplateResponse(
        "employee/feedback.html",
        {
            "request": request,
            "message": "Feedback submitted successfully!",
            "message_type": "success",
        },
    )

@router.get("/sentiments", response_class=HTMLResponse)
async def render_sentiments_page(request: Request, db: Session = Depends(get_db)):
    """Render the sentiment analysis dashboard page"""
    # Get current time and calculate 30 days ago
    utc_time = datetime.now(pytz.utc)
    nepal_time_now = await asyncio.to_thread(convert_utc_to_nepal_local, utc_time)
    thirty_days_ago = nepal_time_now - timedelta(days=30)

    # Query database asynchronously
    feedback_data = await asyncio.to_thread(
        lambda: (
            db.query(
                SupportFeedback.feedback_type,
                SupportFeedback.message,
                SupportFeedback.created_at,
                SupportFeedback.feedback_summary,
                User.full_name
            )
            .join(User, SupportFeedback.user_id == User.user_id)
            .filter(SupportFeedback.created_at >= thirty_days_ago, SupportFeedback.is_deleted == 0)
            .all()
        )
    )

    # Calculate sentiment statistics
    positive_feedback_count = sum(1 for feedback in feedback_data if "Positive" in feedback.feedback_summary)
    negative_feedback_count = len(feedback_data) - positive_feedback_count

    # Calculate sentiment by day for the line chart
    sentiment_by_day = defaultdict(lambda: {'positive': 0, 'negative': 0})
    for feedback in feedback_data:
        feedback_date = feedback.created_at.date()
        if "Positive" in feedback.feedback_summary:
            sentiment_by_day[feedback_date]['positive'] += 1
        else:
            sentiment_by_day[feedback_date]['negative'] += 1

    # Sort dates and prepare chart data
    sorted_dates = sorted(sentiment_by_day.keys())
    sentiment_changes = {
        'dates': [date.strftime('%Y-%m-%d') for date in sorted_dates],
        'positive': [sentiment_by_day[date]['positive'] for date in sorted_dates],
        'negative': [sentiment_by_day[date]['negative'] for date in sorted_dates],
    }

    sentiment_data = {
        'positive': positive_feedback_count,
        'negative': negative_feedback_count,
    }

    # Render template with data
    return templates.TemplateResponse(
        "employee/sentiments.html",
        {
            "request": request,
            "feedback_data": feedback_data,
            "sentiment_data": sentiment_data,
            "sentiment_changes": sentiment_changes,
        },
    )