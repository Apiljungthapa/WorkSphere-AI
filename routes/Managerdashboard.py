from imports import *
import bcrypt # type: ignore
from dotenv import load_dotenv
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

load_dotenv()

@router.get("/manager/{page_name}", response_class=HTMLResponse)
async def manager_page(request: Request, page_name: str):
    return templates.TemplateResponse(f"manager/{page_name}", {"request": request})



@router.get("/register-employee", response_class=HTMLResponse)
async def register_employee_page(request: Request):
    return templates.TemplateResponse("manager/employeeRegister.html", {"request": request})


@router.post("/save-employee")
async def save_employee_details(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):    
    
    hashed_password = Hasher.get_password_hash(password)

    print("________________employee saving code_______________")

    try:
       
        manager = db.query(User).filter(User.role == "manager").first()
        if not manager:
            raise HTTPException(status_code=400, detail="No manager found in the system.")

        manager_email = manager.email

        # Generate credentials
        user_id = generate_unique_user_id(role="employee", db=db)
        otp_code = generate_otp_code()

        # Insert employee record into DB
        new_employee = User(
            user_id=user_id,
            full_name=fullname,
            email=email,
            phone=phone,
            password=hashed_password,
            role="employee",
            department_name=department,
            position=position,
            otp_code=otp_code,
            is_deleted=0
        )

        db.add(new_employee)
        db.commit()

        # Email setup
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = manager_email  
        sender_password = os.getenv("MANAGER_SENDER_PASSWORD") 

        # Create email content
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = "Hello, Welcome to the Team!"

        html_body = f"""
        <html>
        <body>
            <h2>Welcome to the Team!</h2>
            <p>Dear {fullname},</p>
            <p>Your account has been created successfully. Below are your login credentials:</p>
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 60%;">
                <tr><th style="background-color: #f2f2f2;">Email</th><td>{email}</td></tr>
                <tr><th style="background-color: #f2f2f2;">Password</th><td>{password}</td></tr>
                <tr><th style="background-color: #f2f2f2;">OTP Code</th><td>{otp_code}</td></tr>
            </table>
        
            <p>Best Regards,<br>Your Manager<br>{manager.full_name}</p>
        </body>
        </html>
        """

        msg.attach(MIMEText(html_body, "html"))

        # Send email
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Credentials email sent to {email} from Manager ({manager_email})")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to send email: {e}")

        return RedirectResponse(url="/dash", status_code=303)


    except Exception as e:
        print(f"Error: {e}")  # Log the error for debugging
        raise HTTPException(status_code=500, detail=f"Failed to save employee: {e}")
    




@router.get("/dash", response_class=HTMLResponse)
async def fetch_details_employees(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).filter(
        User.is_deleted == 0,  # 0 means not soft-deleted
        User.otp_code.isnot(None),  # Ensure OTP code is not None
        User.otp_code != ""  # Ensure OTP code is not an empty string
    ).all()

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
        "manager/dash.html", 
        {
            "user_id": user_id,
            "request": request,
            "employees": employee_data,
            **department_stats,
        }
    )


@router.get("/tracking.html", response_class=HTMLResponse)
async def tracking_page(request: Request, user_id: str = None, db: Session = Depends(get_db)):

    if user_id:

        employee = db.query(User).filter(User.user_id == user_id, User.is_deleted == '0').first()

        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found")


        query = db.query(Task).filter(
            Task.assigned_to_id == user_id,
            Task.is_deleted == '0',
            Task.is_deleted == None  # Exclude soft-deleted tasks
        )


        pending_tasks = query.filter(Task.status == "Pending").all()

        # Fetch all posts created by the user
        user_posts = db.query(Post).filter(Post.user_id == user_id,Post.is_deleted == '0').all()

        submitted_or_approved_tasks = db.query(Task).filter(
                Task.assigned_to_id == user_id,
                Task.is_deleted == '0',
                Task.status.in_(["submitted", "Approved"])  
            ).all()



        return templates.TemplateResponse(
            "manager/tracking.html",
            {
                "request": request,
                "employee": employee,
                "pending_tasks": pending_tasks,  
                "submitted_or_approved_tasks": submitted_or_approved_tasks, 
                "user_posts": user_posts
            }
        )

    raise HTTPException(status_code=400, detail="No user_id provided")



@router.get("/download/{task_id}")
async def download_file(task_id: str, db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task or not task.docs_path:
        raise HTTPException(status_code=404, detail="File not found")

    file_path = Path(task.docs_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")


    return FileResponse(
        path=file_path,
        filename=file_path.name,  
        media_type="application/octet-stream" 
    )



@router.post("/approve_task")
async def approve_task(task_id: str = Form(...), db: Session = Depends(get_db)):

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")


    task.status = "Approved"
    db.commit()  # Save changes to the database

    
    user_id = task.assigned_to_id


    return RedirectResponse(url=f"/tracking.html?user_id={user_id}", status_code=303)


@router.post("/delete_task/{task_id}")
async def delete_task(task_id: str, user_id: str, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.task_id == task_id, Task.is_deleted == 0).first()

    print(task)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found or already deleted") 
    
    task.is_deleted = 1

    db.commit()

    redirect_url = f"/tracking.html?user_id={user_id}"
    return RedirectResponse(url=redirect_url, status_code=303)



@router.get("/pending_tasks/{user_id}", response_class=HTMLResponse)
async def pending_tasks_page(user_id: str, request: Request, db: Session = Depends(get_db)):

    employee = db.query(User).filter(User.user_id == user_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")


    tasks = db.query(Task).filter(
        Task.assigned_to_id == user_id,  
        Task.is_deleted == None,  
        Task.status == "Pending"  
    ).all()

    return templates.TemplateResponse(
        "manager/tracking.html",
        {
            "request": request,
            "employee": employee,  
            "tasks": tasks, 
        }
    )


@router.get("/updateEmployee.html", response_class=HTMLResponse)
async def update_employee_page(request: Request, user_id: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    return templates.TemplateResponse(
        "manager/updateEmployee.html", 
        {
            "request": request,
            "user": user  
        }
    )


@router.post("/update_personal_detail")
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


@router.get("/delete_user/{user_id}")
async def delete_user(user_id: str, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == False).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found or already deleted")

    # Soft delete user by setting is_deleted = 1
    user.is_deleted = 1

    # Soft delete all related records
    db.query(Post).filter(Post.user_id == user_id).update({"is_deleted": 1})
    db.query(Comment).filter(Comment.user_id == user_id).update({"is_deleted": 1})
    db.query(Like).filter(Like.user_id == user_id).update({"is_deleted": 1})
    db.query(SupportFeedback).filter(SupportFeedback.user_id == user_id).update({"is_deleted": 1})
    db.query(Chatroom).filter(
    (Chatroom.emp1_id == user_id) | (Chatroom.emp2_id == user_id)
    ).update({"is_deleted": '1'})
    db.query(Task).filter(
        (Task.assigned_to_id == user_id) | (Task.assigned_by_id == user_id)
    ).update({"is_deleted": '1'})

    db.query(Message).filter(
        (Message.sender_id == user_id) | (Message.receiver_id == user_id)
    ).update({"is_deleted": '1'})

    db.commit()

    return RedirectResponse(url="/dash", status_code=303)



@router.post("/update_policies")
def update_policies(
    general_guidelines: str = Form(...),
    attendance_policy: str = Form(...),
    leave_policy: str = Form(...),
    working_hours: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Parse JSON string safely
        working_hours_data = json.loads(working_hours)

        # Check if a policy already exists
        policy = db.query(CompanyPolicy).first()

        if policy:
            # Update the existing record
            policy.general_guidelines = general_guidelines
            policy.attendance_policy = attendance_policy
            policy.leave_policy = leave_policy
            policy.working_hours = working_hours_data  # Ensure correct format
        else:
            # No existing record, create a new one (only for the first time)
            policy = CompanyPolicy(
                general_guidelines=general_guidelines,
                attendance_policy=attendance_policy,
                leave_policy=leave_policy,
                working_hours=working_hours_data
            )
            db.add(policy)

        # Save changes to DB
        db.commit()
        db.refresh(policy)

        return RedirectResponse(url="/dash", status_code=303)

    except json.JSONDecodeError:
        return {"error": "Invalid JSON format in working_hours."}




@router.get("/policy", response_class=HTMLResponse)
def get_update_policies(request: Request, db: Session = Depends(get_db)):

    policy = db.query(CompanyPolicy).first()  

    return templates.TemplateResponse("manager/policy.html", {
        "request": request,
        "general_guidelines": policy.general_guidelines if policy else "",
        "attendance_policy": policy.attendance_policy if policy else "",
        "leave_policy": policy.leave_policy if policy else "",
        "working_hours": policy.working_hours if policy else ""
    })


