from config import AI_BASE_DIR
from imports import *
import pytz

router = APIRouter()
templates = Jinja2Templates(directory="templates")

MODEL_DIR = os.path.join(AI_BASE_DIR, "sentimentmodel", "checkpoint-1500")

# Create an instance of SentimentAnalyzer with MODEL_DIR
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
    # Extract user ID from the token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    # Generate a unique feedback ID
    feedback_id = f"FDB{random.randint(10000, 99999)}"

    # Perform sentiment analysis on the full feedback message
    sentiment_result = sentiment_analyzer.predict(message)  

    # Format the sentiment as a percentage
    feedback_summary = f"{sentiment_result['predicted_label']} {sentiment_result['confidence_score']:.2f}%"  

    utc_time = datetime.now(pytz.utc)
    
    nepal_time = convert_utc_to_nepal_local(utc_time)

    # Create a new feedback entry
    new_feedback = SupportFeedback(
        feedback_id=feedback_id,
        user_id=user_id,
        feedback_type=feedbackType,
        message=message,  # Store the full user-entered feedback message
        feedback_summary=feedback_summary,  # Store sentiment analysis result
        created_at=nepal_time,
    )
    db.add(new_feedback)
    db.commit()

    # Prepare a success message
    message = "Feedback submitted successfully!"

    # Render the response template
    return templates.TemplateResponse(
        "employee/feedback.html",
        {
            "request": request,
            "message": message,
            "message_type": "success",
        },
    )



@router.get("/sentiments", response_class=HTMLResponse)
async def render_sentiments_page(request: Request, db: Session = Depends(get_db)):
    """
    Fetch feedback from the last 30 days, joining with the User table to get full_name.
    """
    utc_time = datetime.now(pytz.utc)
    nepal_time_now = convert_utc_to_nepal_local(utc_time)
    thirty_days_ago = nepal_time_now - timedelta(days=30)

    # Fetch feedback with full_name from User table using JOIN on user_id
    feedback_data = (
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

    positive_feedback_count = sum(1 for feedback in feedback_data if "Positive" in feedback.feedback_summary)
    negative_feedback_count = len(feedback_data) - positive_feedback_count  # The rest are negative feedback

    # Prepare sentiment data for the line chart (daily sentiment counts)
    sentiment_by_day = defaultdict(lambda: {'positive': 0, 'negative': 0})
    
    for feedback in feedback_data:
        feedback_date = feedback.created_at.date()
        if "Positive" in feedback.feedback_summary:
            sentiment_by_day[feedback_date]['positive'] += 1
        else:
            sentiment_by_day[feedback_date]['negative'] += 1

    # Sort by date (from 30 days ago to today)
    sorted_dates = sorted(sentiment_by_day.keys())
    sentiment_changes = {
        'dates': [feedback.created_at.strftime('%Y-%m-%d') for feedback in feedback_data],
        'positive': [sentiment_by_day[date]['positive'] for date in sorted_dates],
        'negative': [sentiment_by_day[date]['negative'] for date in sorted_dates],
    }

    # Prepare data for the frontend graph (pie and line chart)
    sentiment_data = {
        'positive': positive_feedback_count,
        'negative': negative_feedback_count,
    }

    # Render the template with the filtered feedback data
    return templates.TemplateResponse(
        "employee/sentiments.html",
        {
            "request": request,
            "feedback_data": feedback_data,
            "sentiment_data": sentiment_data,
            "sentiment_changes": sentiment_changes,
        },
    )