
from imports import *

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/employee/{page_name}", response_class=HTMLResponse)
async def employee_page(request: Request, page_name: str):
    return templates.TemplateResponse(f"employee/{page_name}", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Retrieve the JWT token from cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token_data = decode_access_token(token.replace("Bearer ", ""))
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Extract user data from the token
    user_id = token_data.get("user_id")
    role = token_data.get("role")
    department_name = token_data.get("department_name")

    user = db.query(User).filter(User.user_id == user_id).first()
    user_full_name = user.full_name if user else "Unknown User"

    department_head = db.query(User).filter(
        User.department_name == department_name,
        User.position.ilike('%head%')  
    ).first()  

    department_head_name = department_head.full_name if department_head else "N/A"

    user = db.query(User).filter(User.user_id == user_id).first()
    
    show_red_dot = user.istask_read == "false" or user.isnotificationread == "false"

    # Count members in the same department
    department_members_count = (
        db.query(User).filter(User.department_name == department_name).count()
    )
    print(show_red_dot)

    # Render the dashboard template with the required data
    return templates.TemplateResponse(
        "employee/dashboard.html",
        {
            "request": request,
            "user_id": user_id,
            "user_full_name": user_full_name,
            "role": role,
            "department_name": department_name,
            "department_head": department_head_name,
            "department_members_count": department_members_count,
            "show_red_dot": show_red_dot
        },
    )


@router.get("/emp_details", response_class=HTMLResponse)
async def employee_details_page(request: Request, db: Session = Depends(get_db)):

    # Check for authentication token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Decode token to get user details
    token_data = decode_access_token(token.replace("Bearer ", ""))

    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    department_name = user.department_name

    total_employees = db.query(User).filter(
        User.department_name == department_name, 
        User.role == "employee"
    ).count()

    # Fetch posts for the authenticated user
    posts = fetch_posts_for_user(user_id, db)

    comments = fetch_comments_for_posts(posts, db)

    # Retrieve messages from cookies
    message = request.cookies.get("message")
    message_type = request.cookies.get("message_type")

    # Prepare the template response
    response = templates.TemplateResponse(
        "employee/emp_details.html",
        {
            "user_id":user_id,
            "request": request,
            "posts": posts,
            "message": message,
            "department_name": department_name,
            "total_employees": total_employees,
            "comments_by_post": comments,
            "message_type": message_type,
        },
    )

    # Clear the message cookies after rendering
    response.delete_cookie("message")
    response.delete_cookie("message_type")
    return response




@router.get("/employee-details", response_class=HTMLResponse)
async def employee_details(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    department_name = user.department_name
    if not department_name:
        raise HTTPException(status_code=404, detail="Department not assigned")
    
    # Fetch department heads and add initials
    department_heads = db.query(User).filter(
        User.department_name == department_name,
        User.position.ilike('%head%')  
    ).all()

    department_heads_list = [
        {
            "full_name": head.full_name,
            "initials": generate_initials(head.full_name),  
            "position": head.position
        }
        for head in department_heads
    ]

    

    # Fetch department members and add initials
    department_members = db.query(User).filter(
        User.department_name == department_name,
        ~User.position.ilike('%head%')  
    ).all()

    department_members_list = [
        {
            "full_name": member.full_name,
            "initials": generate_initials(member.full_name),  # Using function
            "position": member.position
        }
        for member in department_members
    ]

    return templates.TemplateResponse("employee/emp_page.html", {
        "request": request,
        "department_name": department_name,
        "department_heads": department_heads_list,
        "department_members": department_members_list
    })


@router.get("/profile", response_class=HTMLResponse)
async def user_profile(request: Request, db: Session = Depends(get_db)):
    # Extract the user ID from the token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    user = db.query(User).filter(User.user_id == user_id).first()
    print(user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse(
        "employee/profile.html",
        {
            "request": request,
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "position": user.position,
        },
    )


@router.post("/update-profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
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

    # Query the user details from the database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user profile
    user.full_name = name
    user.email = email
    user.phone = phone

    db.commit()

    # Redirect back to the profile page with a success message
    return templates.TemplateResponse(
        "employee/profile.html",
        {
            "request": request,
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "position": user.position,
            "message": "Profile updated successfully",
            "message_type": "success",
        },
    )
