from imports import *

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/announcements")
async def get_announcements(request: Request, db: Session = Depends(get_db)):
    
    return templates.TemplateResponse("manager/announcement_form.html", {"request": request})


@router.post("/submit_announcement")
async def submit_announcement(
    request: Request,
    title: str = Form(...),
    date: str = Form(...),
    content: str = Form(...),
    priority: str = Form(...),
    db: Session = Depends(get_db)
):
    while True:
        random_id = f"ANM{random.randint(100, 999)}"
        existing = db.query(Announcement).filter_by(announcement_id=random_id).first()
        if not existing:
            break
    

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
     
    token_data = decode_access_token(token.replace("Bearer ", ""))

    user_id = token_data.get("user_id")

    utc_time = datetime.now(pytz.utc)

    nepal_time = convert_utc_to_nepal_local(utc_time)
    
    # Create new announcement record
    new_announcement = Announcement(
        announcement_id=random_id,
        title=title,
        date=nepal_time,
        content=content,
        priority_level=priority,
        manager_id=user_id  
    )
    
    # Add the new announcement to the database
    db.add(new_announcement)
    db.commit()

    users = db.query(User).all()
    for user in users:
        user.isannouncement_read = "false" 
        user.isnotificationread = "false"

    notification = Notification(
            notification_id=f"NTF{random.randint(1000, 9999)}",
            content="📢 A new announcement has been created. Check out the announcement page!",
            date=nepal_time,
            user_id=None,
            task_id=None
           
            
    )
    db.add(notification)
    db.commit()

    # Return a success message and redirect
    return templates.TemplateResponse(
        "manager/announcement_form.html",
        {
            "request": request,
            "message": f"Announcement '{new_announcement.title}' Created successfully !",
            "message_type": "success"
        }
    )


@router.get("/check_unread_announcements")
async def check_unread_announcements(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id).first()
    return {"unread": user.isannouncement_read == "false"}


@router.get("/view_announcements", response_class=HTMLResponse)
async def view_announcements(
    request: Request, 
    db: Session = Depends(get_db), 
    mark_as_read: bool = Query(False)
):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id).first()

    unread = user and user.isannouncement_read == "false"

    if mark_as_read and user:

        user.isannouncement_read = "true"
        db.commit()
        unread = False  

    announcements = db.query(Announcement).order_by(Announcement.date.desc(), Announcement.priority_level).all()

    return templates.TemplateResponse(
        "employee/see_announcement.html",
        {"request": request, "announcements": announcements, "unread": unread}
    )
