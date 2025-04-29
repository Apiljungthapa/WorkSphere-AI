from imports import *

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/view_notifications")
def view_notifications(request: Request, db: Session = Depends(get_db)):
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    print("ayo hai")

    # Get notifications for this user
    notifications = db.query(Notification).filter(
        (Notification.user_id == user_id) | (Notification.user_id == None)
    ).order_by(Notification.date.desc()).all()

    # Update user's read status
    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.istask_read = True
        user.isnotificationread = True
        db.add(user)

    db.commit()

    return templates.TemplateResponse("employee/notification.html", {"request": request, "notifications": notifications})


@router.get("/mark_notifications_as_read")
def mark_notifications_as_read(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return {"success": False}

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id).first()
    if user:
        user.istask_read = True
        user.isnotification_read = True
        db.add(user)
        db.commit()
        return {"success": True}

    return {"success": False}
