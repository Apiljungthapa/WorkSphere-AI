from imports import *
import pytz # type: ignore
router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/assign-task")
def assign_task(request: Request, db: Session = Depends(get_db)):
    employees = db.query(User).filter(User.role == "Employee").all()
    departments = db.query(User.department_name).distinct().all()
    return templates.TemplateResponse("employee/tasks.html", {
        "request": request,
        "employees": employees,
        "departments": [d[0] for d in departments if d[0] is not None]
    })


@router.post("/assign-task")
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




@router.get("/submission", response_class=HTMLResponse)
async def submission(
    request: Request,
    task_id: str = Query(...),  # Query parameter `task_id` is required
    db: Session = Depends(get_db),
):
    """
    Fetch the task details by task_id and render the submission page.
    Only fetch tasks that are not soft-deleted (is_deleted = 0).
    """

    task = db.query(Task).filter(Task.task_id == task_id, Task.is_deleted == 0).first()

    if not task:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "message": "Task not found or deleted."},
            status_code=404,
        )

    return templates.TemplateResponse(
        "employee/submission.html",
        {
            "request": request,
            "task_id": task.task_id,
            "task_title": task.title,
        },
    )


@router.post("/tasks")
async def create_task(     
    request: Request,
    description: str = Form(...),
    file: UploadFile = File(...),
    task_id: str = Form(...),  
    db: Session = Depends(get_db),
):
    print("Received task id:", task_id)
    
    print("Received description:", description)
    
    print("Received file:", file)
    
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

@router.get("/assignment", response_class=HTMLResponse)
async def assignment(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    tasks = db.query(Task).filter(Task.assigned_to_id == user_id, Task.is_deleted == 0).all()


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
        "employee/assignment.html", 
        {"request": request, "tasks": tasks_with_manager}
    )


# submission udate grne code

@router.get("/update_submission", response_class=HTMLResponse)
async def update_submission(task_id: str, request: Request, db: Session = Depends(get_db)):
    """
    Render the update submission page for a given task.
    """

    
    # Fetch the task from the database
    task = db.query(Task).filter(Task.task_id == task_id).first()
    
    if not task:
        return HTMLResponse(content="Task not found", status_code=404)
    
    return templates.TemplateResponse(
        "employee/update_submission.html",  # Template name
        {
            "request": request,
            "task_id": task.task_id,
            "task_title": task.title,
            "task_description": task.description,
            "previous_docs_path": task.docs_path, 
        }
    )


@router.post("/submit_update")
async def submit_update(
    request: Request,
    task_id: str = Form(...),
    description: str = Form(...),
    previous_docs_path: str = Form(...),
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
    
    # Fetch user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # User directory
    user_dir = create_user_directory(user.user_id, user.full_name)
    if not os.path.exists(user_dir):
        os.makedirs(user_dir)

    # Fetch task
    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update description
    task.description = description

    # File handling
    if file and file.filename:
        file_path = user_dir / file.filename
        with file_path.open("wb") as buffer:
            buffer.write(await file.read())
        task.docs_path = str(file_path)
    else:
        task.docs_path = previous_docs_path  # Use existing path

    db.commit()
    db.refresh(task)

    return RedirectResponse(url="/assignment", status_code=303)
