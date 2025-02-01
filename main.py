from fastapi import FastAPI, Form, Depends, Request, HTTPException, Query, UploadFile, File, Response, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session,sessionmaker
from database import get_db, User, Task, Post, Like, Comment, SupportFeedback, Chatroom, Message, Announcement, Notification
from fastapi.security import OAuth2PasswordBearer
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import uuid
from tasks import send_email_task 
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from fastapi.websockets import WebSocket
from typing import Dict, List
from utils import generate_initials, convert_utc_to_nepal_local
import pytz 

app = FastAPI()
templates = Jinja2Templates(directory="templates")

BASE_DIR = Path("resources")

def generate_unique_user_id(role: str, db: Session) -> str:

    if role == "manager":

        prefix = "MGR"

    else:

        prefix = "EMP"



    # Get the highest existing ID for the role
    last_user = (
        db.query(User)
        .filter(User.role == role)
        .order_by(User.user_id.desc())
        .first()
    )
    if last_user and last_user.user_id.startswith(prefix):
        # Extract numeric part, increment, and format
        last_id_num = int(last_user.user_id[len(prefix):])
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1

    return f"{prefix}{new_id_num:03}"


# Registration form GET route
@app.get("/", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# Registration form POST route to handle the form submission
@app.post("/register", response_class=HTMLResponse)
async def user_register(

    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),

):
    # Check if a manager already exists
    manager_exists = db.query(User).filter(User.role == "manager").first()

    # Assign role
    role = "manager" if not manager_exists else "employee"

    # Generate user ID
    user_id = generate_unique_user_id(role, db)

    # Check if email is already registered
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Email already registered.",
        })

    # Save new user in the database
    new_user = User(
        user_id=user_id,
        full_name=full_name,
        email=email,
        phone=phone,
        password=password,  # Hash password in production
        role=role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Success message
    return templates.TemplateResponse("login.html", {
        "request": request,
        "success": f"{role.capitalize()} registered successfully with ID {user_id}!",
    })


# yaha bata suru vayo ------------------------------------------------


SECRET_KEY = "123##@!%#"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")


@app.post("/login", response_class=HTMLResponse)
async def user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    otp_code: str = Form(...),
    db: Session = Depends(get_db),
):
    # Fetch the user from the database by email
    user = db.query(User).filter(User.email == email).first()

    # Check if user exists
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the entered password matches the one stored in the database
    if user.password != password:
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Verify OTP
    if user.otp_code != otp_code:
        raise HTTPException(status_code=401, detail="Incorrect OTP")

    # Generate a JWT token with user's role and department details
    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "role": user.role,
            "department_name": user.department_name,
        }
    )

    # Redirect based on role
    if user.role == "manager":
        response = RedirectResponse(url="/dash", status_code=303)
    elif user.role == "employee":
        response = RedirectResponse(url="/dashboard", status_code=303)
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


# ---------------------------------------------------------------------------------

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")



@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Retrieve the JWT token from cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Decode the JWT token to get user information
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
        User.position.ilike('%head%')  # Case-insensitive match for "head"
    ).first()  # Retrieve the first matching record

    # print("ds",department_head)

    department_head_name = department_head.full_name if department_head else "N/A"

    user = db.query(User).filter(User.user_id == user_id).first()
    
    # Show red dot if any notification is unread
    show_red_dot = user.istask_read == "false" or user.isnotificationread == "false"



    # Count members in the same department
    department_members_count = (
        db.query(User).filter(User.department_name == department_name).count()
    )
    print(show_red_dot)

    # Render the dashboard template with the required data
    return templates.TemplateResponse(
        "dashboard.html",
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


# -------------------------------------------------------------------------------------





# @app.get("/dashboard", response_class=HTMLResponse)
# async def employee_dashboard(request: Request):
#     return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/employee", response_class=HTMLResponse)
async def fetch_incomplete_users(request: Request, db: Session = Depends(get_db)):

    incomplete_users = db.query(User).filter(
        (User.otp_code == None) & (User.department_name == None) & (User.position == None)
    ).with_entities(User.email, User.phone, User.full_name, User.user_id).all()

    return templates.TemplateResponse("employee.html", {
        "request": request,
        "users": incomplete_users,
    })



@app.post("/delete-user", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: str = Form(...), db: Session = Depends(get_db)):

    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    incomplete_users = db.query(User).filter(
        (User.otp_code == None) & (User.department_name == None) & (User.position == None)
    ).with_entities(User.email, User.phone, User.full_name, User.user_id).all()

    return templates.TemplateResponse("employee.html", {
        "request": request,
        "users": incomplete_users,
    })


@app.get("/edit/{user_id}", response_class=HTMLResponse)
async def edit_employee(user_id: str, request: Request, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("updateEmployee.html", {
        "request": request,
        "user": user,
    })


# quque gareko wala code ho yo..

# @app.post("/update-employee")
# async def update_employee(
#     user_id: str = Form(...),
#     department: str = Form(...),
#     position: str = Form(...),
#     db: Session = Depends(get_db),
# ):
#     # Fetch user from database
#     user = db.query(User).filter(User.user_id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Update user details and generate OTP
#     user.department_name = department
#     user.position = position
#     otp_code = random.randint(100000, 999999)
#     user.otp_code = otp_code
#     db.commit()

#     # Enqueue email task
#     send_email_task.delay(user.email, user.full_name, otp_code)

#     return RedirectResponse(url="/dash", status_code=303)





@app.post("/update-employee")
async def update_employee(
    user_id: str = Form(...),
    department: str = Form(...),
    position: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.department_name = department
    user.position = position

    otp_code = random.randint(100000, 999999)
    user.otp_code = otp_code
    db.commit()

    # Send OTP via email using SendGrid
    message = Mail(
        from_email='apilthapa87@gmail.com',  # Manager's email
        to_emails=user.email,
        subject='Your OTP Code',
        html_content=f'<strong>Hello {user.full_name}, your OTP code is {otp_code}. Please enter this while logging in. </strong>'
    )

    try:
        sg = SendGridAPIClient('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')
        sg.send(message)
        
    except Exception as e:
        print(f"Error sending email: {e}")

    return RedirectResponse(url="/dash", status_code=303)



# aba task ko suru vayo hai

@app.get("/assign-task")
def assign_task(request: Request, db: Session = Depends(get_db)):
    employees = db.query(User).filter(User.role == "Employee").all()
    departments = db.query(User.department_name).distinct().all()
    return templates.TemplateResponse("tasks.html", {
        "request": request,
        "employees": employees,
        "departments": [d[0] for d in departments if d[0] is not None]
    })


def generate_task_id():
    prefix = "TSK"
    unique_id = ''.join(random.choices(string.digits, k=3))  
    return f"{prefix}{unique_id}"


@app.post("/assign-task")
def assign_task(
    request: Request,
    title: str = Form(...),
    assigned_to_id: str = Form(...),
      
    dueDate: str = Form(...),
    db: Session = Depends(get_db),
):

    task_id = generate_task_id()

    manager_id = "MGR001"  

    task = Task(

        task_id=task_id,
        title=title,
        description="",  
        due_date=dueDate,
        docs_path=None, 
        status="Pending",  
        assigned_to_id=assigned_to_id,
        assigned_by_id=manager_id,

    )

    db.add(task)

    user = db.query(User).filter(User.user_id == assigned_to_id).first()
    if user:
        user.istask_read = "false"  # Store as string, not Boolean
        db.add(user)
        db.commit()


    utc_time = datetime.now(pytz.utc)

    nepal_time = convert_utc_to_nepal_local(utc_time)

    notification_id=f"NTF{random.randint(1000, 9999)}",



    notification = Notification(
        notification_id=notification_id,
        user_id=assigned_to_id, 
        date=nepal_time,
        task_id=task_id,
        content=f"New task assigned: {title}, Check it out!",
        
    )
    db.add(notification)

    db.commit()

    return RedirectResponse(url="/dash", status_code=303)




@app.get("/submission", response_class=HTMLResponse)
async def submission(
    request: Request,
    task_id: str = Query(...),  # Query parameter `task_id` is required
    db: Session = Depends(get_db),
):
    """
    Fetch the task details by task_id and render the submission page.
    """

    task = db.query(Task).filter(Task.task_id == task_id).first()

    if not task:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Task not found."},
            status_code=404,
        )

    return templates.TemplateResponse(
        "submission.html",
        {
            "request": request,
            "task_id": task.task_id,
            "task_title": task.title,
        },
    )

def create_user_directory(user_id: int, full_name: str) -> Path:
    """
    Creates a directory for the user if it does not exist.
    Folder name is based on user_id and full_name.
    """
    user_dir = BASE_DIR / f"{user_id}_{full_name.replace(' ', '_')}"
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


@app.post("/tasks")
async def create_task(     
    request: Request,
    description: str = Form(...),
    file: UploadFile = File(...),
    task_id: str = Form(...),  
    db: Session = Depends(get_db),
):
    print("Received task id:", task_id)
    
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))  
    user_id = token_data.get("user_id")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_dir = create_user_directory(user.user_id, user.full_name)
    
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    file_path = user_dir / file.filename
    with file_path.open("wb") as buffer:
        buffer.write(await file.read())  

    task = db.query(Task).filter(Task.task_id == task_id).first()

    if task:

        task.description = description
        task.docs_path = str(file_path)
        task.status = "submitted"  

        db.commit() 
        db.refresh(task) 
        return RedirectResponse(url="/assignment", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="Task not found")

# ----------------------------------------------------------------

# task fetch grne user login jo xa tesko

@app.get("/assignment", response_class=HTMLResponse)
async def assignment(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    tasks = db.query(Task).filter(Task.assigned_to_id == user_id).all()

    tasks_with_manager = []
    for task in tasks:
        if task.assigned_by:
            manager = db.query(User).filter(User.user_id == task.assigned_by.user_id).first()
            manager_name = manager.full_name if manager else "Unknown Manager"
        else:
            manager_name = "No Manager Assigned"
        
        tasks_with_manager.append({

            "task_id": task.task_id,
            "task_title": task.title,
            "description": task.description,
            "due_date": task.due_date,
            "docs_path": task.docs_path,
            "status": task.status,  
            "assigned_by": manager_name,
        })

    return templates.TemplateResponse(
        "assignment.html", 
        {"request": request, "tasks": tasks_with_manager}
    )


# submission udate grne code

@app.get("/update_submission", response_class=HTMLResponse)
async def update_submission(task_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Render the update submission page for a given task.
    """

    
    # Fetch the task from the database
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return HTMLResponse(content="Task not found", status_code=404)
    
    return templates.TemplateResponse(
        "update_submission.html",  # Template name
        {
            "request": request,
            "task_id": task.task_id,
            "task_title": task.title,
            "task_description": task.description,
            "previous_docs_path": task.docs_path, 
        }
    )



@app.post("/submit_update")
async def submit_update(
    request: Request,
    task_id: str = Form(...),
    description: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    """
    Handle task update submission.
    """

    # Authenticate the user
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    
    # Fetch the user from the database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create user directory if it doesn't exist
    user_dir = create_user_directory(user.user_id, user.full_name)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
    
    # Fetch the task by task_id
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update the description
    task.description = description
    
    # Handle the file upload if provided
    if file:
        file_path = user_dir / file.filename  # Save in the user-specific directory
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())
        

        task.docs_path = str(file_path)
    

    db.commit()
    db.refresh(task)  
    

    return RedirectResponse(url="/assignment", status_code=303)





# -----------------------------------------------------------------------
# post fetch garera dekhaune
@app.get("/emp_details", response_class=HTMLResponse)
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
        "emp_details.html",
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







@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.get("/editpost", response_class=HTMLResponse)
async def post_edit_page(request: Request):
    return templates.TemplateResponse("post_edit.html", {"request": request})



@app.get("/employee-details", response_class=HTMLResponse)
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
            "initials": generate_initials(head.full_name),  # Using function
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

    return templates.TemplateResponse("emp_page.html", {
        "request": request,
        "department_name": department_name,
        "department_heads": department_heads_list,
        "department_members": department_members_list
    })

# post banaune ayo

@app.post("/posts/")
async def create_post(request: Request, title: str = Form(...), content: str = Form(...), db: Session = Depends(get_db)):

    try:

        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        token_data = decode_access_token(token.replace("Bearer ", ""))

        user_id = token_data.get("user_id")

        post_id = f"PST{str(uuid.uuid4().int)[:5]}"

        utc_time = datetime.now(pytz.utc)
        nepal_time = convert_utc_to_nepal_local(utc_time)


        db_post = Post(
            post_id=post_id,
            title=title,
            content=content,
            created_date=nepal_time,
            user_id=user_id  
        )
        db.add(db_post)
        db.commit()
        db.refresh(db_post)

        posts = fetch_posts_for_user(user_id, db) # call gareko func lai

        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Post created successfully!")
        response.set_cookie("message_type", "success")
        return response
    
    except SQLAlchemyError as e:
        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Failed to create the post!")
        response.set_cookie("message_type", "error")
        return response
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")





def fetch_posts_for_user(user_id: str, db: Session) -> list:
    """
    Fetch posts for a user based on their department, excluding soft deleted posts, and including like status.
    Also fetches the created_date formatted to "YYYY-MM-DD HH:MM:SS".
    """
    # Fetch the user from the database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the user's department
    current_user_department = user.department_name

    posts = db.query(Post).join(User).filter(
        User.department_name == current_user_department,
        Post.deleted_at == 0  
    ).all()


    for post in posts:

        is_liked = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post.post_id).first() is not None
        post.is_liked = is_liked
        author = db.query(User).filter(User.user_id == post.user_id).first()
        full_name = author.full_name if author else "Unknown"
        initials = generate_initials(full_name)

        if post.created_date:
            post.created_date = post.created_date.strftime("%B %d, %Y %I:%M %p")

        post.full_name = full_name
        post.initials = initials

    return posts





# post edit garda id pathaune  

@app.get("/post/edit/{post_id}", response_class=HTMLResponse)
async def post_edit_page(post_id: str, request: Request, db: Session = Depends(get_db)):

    post = db.query(Post).filter(Post.post_id == post_id).first()
    

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse(
        "post_edit.html",
        {
            "request": request,
            "post": post,  
        },
    )


# post update garne code

@app.post("/edit_post/{post_id}", response_class=HTMLResponse)
async def edit_post(
    request: Request,
    post_id: str,
    content: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        # Fetch the post by post_id
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")


        post.content = content.strip()  # Trim whitespace to avoid unintended issues
        db.commit()  # Save changes to the database
        db.refresh(post)  # Refresh the session to reflect updated changes
        print("Update successful")

        # Redirect with success message
        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Post updated successfully!")
        response.set_cookie("message_type", "success")
        return response

    except Exception as e:
        print(f"Error during update: {e}")  # Log the exception
        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Failed to update the post!")
        response.set_cookie("message_type", "error")
        return response



@app.get("/post/delete/{post_id}", response_class=RedirectResponse)
async def soft_delete_post(post_id: str, request: Request, db: Session = Depends(get_db)):

    try:
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post.deleted_at = 1  
        db.commit()

        # Set success message in cookies
        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Post deleted successfully!")
        response.set_cookie("message_type", "success")
        return response
    except Exception as e:
        print(f"Error during deletion: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete the post")
    




#Likes ko part ayo aba..

@app.post("/post/{action}/{post_id}")
def toggle_like(action: str, post_id: str, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post_id).first()

    if action == "like":

        if not existing_like:
            like_id = f"LKE{random.randint(1000, 9999)}"
            new_like = Like(like_id=like_id, user_id=user_id, post_id=post_id)
            db.add(new_like)

            post.likes += 1
            db.commit()

    elif action == "unlike":

        if existing_like:
            db.delete(existing_like)


            post.likes -= 1
            db.commit()

    db.refresh(post)
    return {"likes": post.likes}  


# comment
@app.post("/comments/")
async def add_comment(
    request: Request, 
    post_id: str = Form(...),  
    content: str = Form(...), 
    db: Session = Depends(get_db) 
):
    try:
        # Check for token authentication
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        token_data = decode_access_token(token.replace("Bearer ", ""))
        user_id = token_data.get("user_id")

        # Generate unique comment_id (e.g., cmnt0934)
        comment_id = f"cmnt{str(uuid.uuid4().int)[:5]}"  # Generate random comment_id using UUID

        utc_time = datetime.now(pytz.utc)
        nepal_time = convert_utc_to_nepal_local(utc_time)

        
        # Create the Comment instance using SQLAlchemy ORM
        new_comment = Comment(
            comment_id=comment_id,
            content=content,
            post_id=post_id,  
            comment_date=nepal_time,
            user_id=user_id
        )

        # Add the comment to the session and commit
        db.add(new_comment)
        db.commit()

        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Comment added successfully!")
        response.set_cookie("message_type", "success")
        return response

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



def fetch_comments_for_posts(posts: list, db: Session) -> dict:
    
    post_ids = [post.post_id for post in posts]
    comments = (
        db.query(Comment, User.full_name)
        .join(User, User.user_id == Comment.user_id)
        .filter(Comment.post_id.in_(post_ids))
        .all()
    )

    # Organize comments by post_id
    comments_by_post = {}
    for comment, full_name in comments:
        initials = generate_initials(full_name)
        if comment.post_id not in comments_by_post:
            comments_by_post[comment.post_id] = []
        comments_by_post[comment.post_id].append(
            {
                "content": comment.content,
                "full_name": full_name,
                "initials": initials,
                "comment_date": comment.comment_date.strftime("%B %d, %Y %I:%M %p"),
            }
        )
    return comments_by_post




# aba manager ko perspecive bata suru vyo

@app.get("/dash", response_class=HTMLResponse)
async def fetch_details_employees(request: Request, db: Session = Depends(get_db)):

    users = db.query(User).filter(User.is_deleted == False).all()


    unique_departments = {user.department_name for user in users if user.department_name}


    employee_data = [
        {
            "user_id": user.user_id,
            "name": user.full_name,
            "position": user.position,
            "department": user.department_name
        }
        for user in users if user.role == 'employee'  # Only include employees
    ]


    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    role = token_data.get("role")


    if role != "manager":

        employee_data = [
            employee for employee in employee_data if employee["department"] == token_data.get("department")
        ]
    

    department_stats = {
        "total_employees": len(employee_data),
        "total_departments": len(unique_departments),
    }


    return templates.TemplateResponse(
        "dash.html", 
        {
            "user_id": user_id,
            "request": request,
            "employees": employee_data,
            **department_stats,
        }
    )





@app.get("/tracking.html", response_class=HTMLResponse)
async def tracking_page(request: Request, user_id: str = None, db: Session = Depends(get_db)):

    if user_id:

        employee = db.query(User).filter(User.user_id == user_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")


        query = db.query(Task).filter(
            Task.assigned_to_id == user_id,  # Tasks assigned to the user
            Task.deleted_at == None  # Exclude soft-deleted tasks
        )


        pending_tasks = query.filter(Task.status == "Pending").all()

        # Fetch all posts created by the user
        user_posts = db.query(Post).filter(Post.user_id == user_id).all()

        submitted_or_approved_tasks = db.query(Task).filter(
                Task.assigned_to_id == user_id,
                Task.deleted_at == None,  # Exclude soft-deleted tasks
                Task.status.in_(["submitted", "Approved"])  # Only submitted or approved tasks
            ).all()



        return templates.TemplateResponse(
            "tracking.html",
            {
                "request": request,
                "employee": employee,
                "pending_tasks": pending_tasks,  
                "submitted_or_approved_tasks": submitted_or_approved_tasks, 
                "user_posts": user_posts
            }
        )

    raise HTTPException(status_code=400, detail="No user_id provided")






@app.get("/download/{task_id}")
async def download_file(task_id: str, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task or not task.docs_path:
        raise HTTPException(status_code=404, detail="File not found")


    file_path = Path(task.docs_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")


    return FileResponse(
        path=file_path,
        filename=file_path.name,  # Original file name
        media_type="application/octet-stream"  # MIME type
    )



@app.post("/approve_task")
async def approve_task(task_id: str = Form(...), db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")


    task.status = "Approved"
    db.commit()  # Save changes to the database

    
    user_id = task.assigned_to_id


    return RedirectResponse(url=f"/tracking.html?user_id={user_id}", status_code=303)



@app.post("/delete_task/{task_id}")

async def delete_task(task_id: str, user_id: str, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.task_id == task_id, Task.deleted_at == None).first()

    if not task:
        
        raise HTTPException(status_code=404, detail="Task not found or already deleted") 


    task.deleted_at = datetime.now(timezone.utc)

    db.commit()


    redirect_url = f"/tracking.html?user_id={user_id}"
    return RedirectResponse(url=redirect_url, status_code=303)


@app.get("/pending_tasks/{user_id}", response_class=HTMLResponse)
async def pending_tasks_page(user_id: str, request: Request, db: Session = Depends(get_db)):
    # Fetch employee details
    employee = db.query(User).filter(User.user_id == user_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")


    tasks = db.query(Task).filter(
        Task.assigned_to_id == user_id,  # Tasks assigned to the user
        Task.deleted_at == None,  
        Task.status == "Pending"  
    ).all()


    return templates.TemplateResponse(
        "tracking.html",
        {
            "request": request,
            "employee": employee,  
            "tasks": tasks,  # Include only pending tasks
        }
    )


@app.get("/updateEmployee.html", response_class=HTMLResponse)
async def update_employee_page(request: Request, user_id: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return templates.TemplateResponse(
        "updateEmployee.html", 
        {
            "request": request,
            "user": user  # Pass user data to the template
        }
    )

@app.post("/update_personal_detail")
async def update_personal_detail(request: Request, db: Session = Depends(get_db)):
    # Get the form data
    form = await request.form()
    user_id = form.get("user_id")
    department = form.get("department")
    position = form.get("position")


    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")


    user.department_name = department
    user.position = position


    db.commit()


    return RedirectResponse(url=f"/tracking.html?user_id={user_id}", status_code=303)




@app.get("/delete_user/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    Soft delete a user by setting is_deleted to True and recording the deleted_at timestamp.
    """
    # Find the user in the database
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()

    print("ds", user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    # Soft delete the user
    user.is_deleted = True
    user.deleted_at = datetime.now(timezone.utc)  # Record deletion timestamp
    db.commit()

    # Redirect back to the tracking page
    return RedirectResponse(url="/dash", status_code=303)


@app.get("/feedback", response_class=HTMLResponse)
async def feedback_page(request: Request, db: Session = Depends(get_db)):
    # Here you can fetch any necessary data, or handle feedback form processing

    # Prepare the template response
    return templates.TemplateResponse("feedback.html", {"request": request})


@app.post("/submit-feedback", response_class=HTMLResponse)
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


    
    
    # Create a new feedback entry
    new_feedback = SupportFeedback(
        feedback_id=feedback_id,
        user_id=user_id,
        feedback_type=feedbackType,
        message=message,
        created_at=datetime.now(timezone.utc),
    )
    db.add(new_feedback)
    db.commit()

    # Prepare a success message
    message = "Feedback submitted successfully "

    # Render the response template
    return templates.TemplateResponse(
        "feedback.html",
        {
            "request": request,
            "message": message,
            "message_type": "success",
        },
    )



@app.get("/sentiments", response_class=HTMLResponse)
async def render_sentiments_page(request: Request, db: Session = Depends(get_db)):
    """
    Fetch all feedback data from the `support_feedback` table and render the sentiments.html page.
    """
    # Query the support_feedback table for feedback_type, message, and created_at
    feedback_data = db.query(SupportFeedback.feedback_type, SupportFeedback.message, SupportFeedback.created_at).all()

    # Render the template with the feedback data
    return templates.TemplateResponse(
        "sentiments.html",
        {
            "request": request,
            "feedback_data": feedback_data,  # Pass the feedback data to the template
        },
    )







@app.get("/profile", response_class=HTMLResponse)
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
        "profile.html",
        {
            "request": request,
            "name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "position": user.position,
        },
    )


@app.post("/update-profile", response_class=HTMLResponse)
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
        "profile.html",
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



# chatting <<<<<---------------------------------------------->>>>>>>>>>>>>>


@app.get("/feed", response_class=HTMLResponse)
async def get_feed(request: Request, db: Session = Depends(get_db)):
    
    # Get the access token from the request cookies
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Decode the JWT token to get the logged-in user's ID
        token_data = decode_access_token(token.replace("Bearer ", ""))
        logged_in_user_id = token_data.get("user_id")

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(User).filter(User.user_id == logged_in_user_id).first()

    role = user.role

    back_url = "/emp_details" if role == "employee" else "/dash"

    # Query the database for all users except the logged-in user
    users = db.query(User.user_id, User.full_name).filter(User.user_id != logged_in_user_id).all()

    

    users_with_initials = []
    for user in users:
        unread_count = db.query(Message).filter(
            Message.sender_id == user.user_id,
            Message.receiver_id == logged_in_user_id,
            Message.status == 'unread'
        ).count()
        users_with_initials.append({
            "user_id": user.user_id,
            "full_name": user.full_name,
            "initials": generate_initials(user.full_name),
            "unread_count": unread_count
        })

    return templates.TemplateResponse(
        "feed.html",
        {
            "request": request,
            "users": users_with_initials,
            "logged_in_user_id": logged_in_user_id,
            "back_url": back_url 
        }
    )



@app.get("/chatting")
async def chatting(emp2_id: str, request: Request, db: Session = Depends(get_db)):
    # Get emp1_id from the token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Decode the JWT token to get emp1_id
        token_data = decode_access_token(token.replace("Bearer ", ""))
        emp1_id = token_data.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    print(emp2_id)

  

    # Check if a chatroom exists between emp1 and emp2
    chatroom = (
        db.query(Chatroom)
        .filter(
            ((Chatroom.emp1_id == emp1_id) & (Chatroom.emp2_id == emp2_id)) |
            ((Chatroom.emp1_id == emp2_id) & (Chatroom.emp2_id == emp1_id))
        )
        .first()
    )

    if chatroom:
        db.query(Message).filter(
            Message.chat_id == chatroom.chat_id,
            Message.sender_id == emp2_id,
            Message.receiver_id == emp1_id,
            Message.status == 'unread'
        ).update({"status": "read"})
        db.commit()

    else:
        # Generate a random unique chat ID
        chat_id = "CHT" + "".join(random.choices(string.digits, k=8))
        
        # Create a new chatroom
        chatroom = Chatroom(
            chat_id=chat_id,
            emp1_id=emp1_id,
            emp2_id=emp2_id,
            created_date=datetime.now(timezone.utc)
        )
       
        db.add(chatroom)
        db.commit()
        db.refresh(chatroom)

    # Fetch emp1 and emp2 names
    emp1_name = db.query(User).filter(User.user_id == emp1_id).first().full_name
    emp2_name = db.query(User).filter(User.user_id == emp2_id).first().full_name
    emp2_initials = generate_initials(emp2_name)  

    # Render the chatroom details in the template
    return templates.TemplateResponse(
        "chatting.html",
        {
            "request": request,
            "chatroom_id": chatroom.chat_id,
            "emp2_name": emp2_name,
            "emp2_initials": emp2_initials,  
            "emp1_id": emp1_id,
            "emp2_id": emp2_id
        }
    )



# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            websocket = self.active_connections[user_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for websocket in self.active_connections.values():
            await websocket.send_json(message)
    

manager = ConnectionManager()


@app.get("/total_unread")
async def get_total_unread(request: Request, db: Session = Depends(get_db)):
    # Get user_id from the token
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Decode the JWT token to get user_id
        token_data = decode_access_token(token.replace("Bearer ", ""))
        user_id = token_data.get("user_id")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Count total unread messages for the logged-in user
    total_unread = db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.status == 'unread'
    ).count()
    
    return {"total_unread": total_unread}



# WebSocket Endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, db: Session = Depends(get_db)):
    await manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()

            chat_id = data["chat_id"]
            sender_id = data["sender_id"]
            receiver_id = data["receiver_id"]
            content = data["content"]
            
            # Get the current UTC time and convert to Nepal time
            utc_time = datetime.now(pytz.utc)
            nepal_time = convert_utc_to_nepal_local(utc_time)

            msg_id = "MSG" + "".join(random.choices(string.digits, k=4))

            # Save message to database with Nepal time
            message = Message(
                msg_id=msg_id,
                chat_id=chat_id,
                status='unread',
                sender_id=sender_id,
                receiver_id=receiver_id,
                content=content,
                timestamp=nepal_time  
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            # Send message to receiver (send Nepal time in response)
            response = {
                "type": "chat_message",
                "chat_id": chat_id,
                "sender_id": sender_id,
                "receiver_id": receiver_id,
                "content": content,
                "timestamp": nepal_time.isoformat()  
            }

            await manager.send_personal_message(response, receiver_id)
            

            unread_count = db.query(Message).filter(
                Message.sender_id == sender_id,
                Message.receiver_id == receiver_id,
                Message.status == 'unread'
            ).count()

            # Send notification to receiver's feed
            notification = {
                "type": "new_message",
                "sender_id": sender_id,
                "unread_count": unread_count,
                
            }

            await manager.broadcast(notification)
            

            # Send message to sender
            await manager.send_personal_message(notification, receiver_id)

    except WebSocketDisconnect:
        manager.disconnect(user_id)



# Fetch Chat History API
@app.get("/chats/{chat_id}")
def get_chat_history(chat_id: str, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(Message.chat_id == chat_id).order_by(Message.timestamp.asc()).all()
    return [
        {
            "msg_id": message.msg_id,
            "content": message.content,
            "status": message.status,
            "timestamp": message.timestamp.isoformat(),
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id
        }
        for message in messages
    ]

# <<<<<<<<<<<<<--------------------------------------------------------------->>>>>>>>>>>>>.








# ----------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# announcement
@app.get("/announcements")
async def get_announcements(request: Request, db: Session = Depends(get_db)):
    
    return templates.TemplateResponse("announcement_form.html", {"request": request})




  






@app.post("/submit_announcement")
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
        "announcement_form.html",
        {
            "request": request,
            "message": f"Announcement '{new_announcement.title}' Created successfully !",
            "message_type": "success"
        }
    )







@app.get("/check_unread_announcements")
async def check_unread_announcements(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id).first()
    return {"unread": user.isannouncement_read == "false"}







@app.get("/view_announcements", response_class=HTMLResponse)
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
        unread = False  # Since we marked it as read

    announcements = db.query(Announcement).order_by(Announcement.date.desc(), Announcement.priority_level).all()

    return templates.TemplateResponse(
        "see_announcement.html",
        {"request": request, "announcements": announcements, "unread": unread}
    )




# notifications ko suru vayo hai
@app.get("/view_notifications")
def view_notifications(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

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

    return templates.TemplateResponse("notification.html", {"request": request, "notifications": notifications})





@app.get("/mark_notifications_as_read")
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








# ----------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>




@app.get("/logout")
async def logout(response: Response):
    # Remove the JWT token by setting its expiration time to the past
    response.delete_cookie("access_token")  # Assuming your JWT token is stored in 'access_token' cookie

    # Redirect the user to the login page
    return RedirectResponse(url="/login")