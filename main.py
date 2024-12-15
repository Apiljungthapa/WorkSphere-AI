from fastapi import FastAPI, Form, Depends, Request, HTTPException, Query, UploadFile, File, Response
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db, User, Task
from fastapi.security import OAuth2PasswordBearer
import random
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import random
import string
from typing import List
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import uuid
from tasks import send_email_task 
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles

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

# @app.get("/dash", response_class=HTMLResponse)
# async def dash(request: Request):

#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=401, detail="Not authenticated")
    
#     token_data = decode_access_token(token.replace("Bearer ", ""))
#     user_id = token_data.get("user_id")
#     role = token_data.get("role")

#     return templates.TemplateResponse("dash.html", {"request": request, "user_id": user_id, "role": role})

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

    department_head = db.query(User).filter(
        User.department_name == department_name,
        User.position.ilike('%head%')  # Case-insensitive match for "head"
    ).first()  # Retrieve the first matching record

    # print("ds",department_head)

    department_head_name = department_head.full_name if department_head else "N/A"


    # Count members in the same department
    department_members_count = (
        db.query(User).filter(User.department_name == department_name).count()
    )

    # Render the dashboard template with the required data
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_id": user_id,
            "role": role,
            "department_name": department_name,
            "department_head": department_head_name,
            "department_members_count": department_members_count,
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
        
        # Update the file path in the database
        task.docs_path = str(file_path)
    
    # Save updates in the database
    db.commit()
    db.refresh(task)  # Refresh to reflect the latest changes
    
    # Redirect to the assignment page
    return RedirectResponse(url="/assignment", status_code=303)





# -----------------------------------------------------------------------

@app.get("/emp_details", response_class=HTMLResponse)
async def employee_details_page(request: Request):
    return templates.TemplateResponse("emp_details.html", {"request": request})





@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


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
    
    department_heads = db.query(User).filter(
        User.department_name == department_name,
        User.position.ilike('%head%')  
    ).all()
    
    department_members = db.query(User).filter(
        User.department_name == department_name,
        ~User.position.ilike('%head%') 
    ).all()

    
    return templates.TemplateResponse("emp_page.html", {
        "request": request,
        "department_name": department_name,
        "department_heads": department_heads,
        "department_members": department_members
    })




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
                "pending_tasks": pending_tasks,  # Tasks with "Pending" status
                "submitted_or_approved_tasks": submitted_or_approved_tasks,  # Tasks with "Submitted" or "Approved" status
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










@app.get("/logout")
async def logout(response: Response):
    # Remove the JWT token by setting its expiration time to the past
    response.delete_cookie("access_token")  # Assuming your JWT token is stored in 'access_token' cookie

    # Redirect the user to the login page
    return RedirectResponse(url="/login")