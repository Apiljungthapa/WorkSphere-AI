from imports import *
import bcrypt # type: ignore

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
   
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/ishPage", response_class=HTMLResponse)
async def Ish_page(request: Request):
    return templates.TemplateResponse("ishPage.html", {"request": request})


@router.post("/ishDetails", response_class=HTMLResponse)
async def send_ishDetails_page(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    position: str = Form(...),
    department: str = Form(...),
    db: Session = Depends(get_db),
):

    hr_user = db.query(User).filter(User.role == 'HR').first()
    if not hr_user:
        return {"error": "HR user not found"}

    hr_email = hr_user.email  # HR's email (this will be the 'From' address)

    manager_user = db.query(User).filter(User.role == 'manager').first()
    if not manager_user:
        return {"error": "Manager user not found"}

    manager_email = manager_user.email  # Manager's email (this will be the 'To' address)

    print(f"Sending from HR: {hr_email} to Manager: {manager_email}")

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = hr_email  
    sender_password = "qiromvjkgibjqipy"  

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = manager_email
    msg["Subject"] = "New Employee Details Submission"

    # HTML table content
    html_body = f"""
    <html>
    <body>
        <h2>New Employee Details Submitted by HR</h2>
        <p>Dear Manager,</p>
        <p>Please find the details of the newly submitted employee below:</p>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 60%;">
            <tr><th style="background-color: #f2f2f2;">Full Name</th><td>{fullname}</td></tr>
            <tr><th style="background-color: #f2f2f2;">Email Address</th><td>{email}</td></tr>
            <tr><th style="background-color: #f2f2f2;">Phone Number</th><td>{phone}</td></tr>
            <tr><th style="background-color: #f2f2f2;">Position</th><td>{position}</td></tr>
            <tr><th style="background-color: #f2f2f2;">Department</th><td>{department if department else 'N/A'}</td></tr>
        </table>
        <p>Kindly review and proceed further.</p>
        <p>Best Regards,<br>HR Department</p>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        print(f"Email sent successfully from HR ({hr_email}) to Manager ({manager_email})")
    except Exception as e:
        print(f"Error sending email: {e}")
    finally:
        server.quit()

    # Log for debugging
    print(f"Received form data: Fullname={fullname}, Email={email}, Phone={phone}, Position={position}, Department={department}")

    return RedirectResponse(url='/', status_code=303)


@router.get("/check_email")
async def check_email(email: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email, User.role == 'HR').first()
    
    if user:
        return JSONResponse(content={"exists": True})
    else:
        return JSONResponse(content={"exists": False})


@router.post("/login", response_class=HTMLResponse)
async def user_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    otp_code: str = Form(...),
    db: Session = Depends(get_db),
):    
    user = db.query(User).filter(
        User.email.like(f"%{email}%"),
        User.is_deleted == 0
    ).first()

    print(user)


    # Check if user exists and is not deleted
    if user is None:
        raise HTTPException(status_code=404, detail="User not found or account deleted")
    
    if user.role == "manager":

        if not Hasher.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")
    
    elif user.role == "employee":

        if not Hasher.verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password employee")
    
    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")
    

    # Verify OTP
    if user.otp_code != otp_code:
        raise HTTPException(status_code=401, detail="Incorrect OTP")

    access_token = create_access_token(
        data={
            "user_id": user.user_id,
            "role": user.role,
            "department_name": user.department_name,
        }
    )

    print("Access Token:", access_token)

    if user.role == "manager":
        response = RedirectResponse(url="/dash", status_code=303)

    elif user.role == "employee":
        response = RedirectResponse(url="/dashboard", status_code=303)

    else:
        raise HTTPException(status_code=403, detail="Unauthorized role")

    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, samesite="Lax", secure=False)

    return response


@router.post("/create-hr")
async def create_hr_user(db: Session = Depends(get_db)):
    try:
        hr_user = ManagerHRManager.create_hr_user(db)
        return {"message": "HR user created successfully", "user": hr_user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create HR user: {str(e)}")

@router.post("/create-manager")
async def create_manager_user(db: Session = Depends(get_db)):
    try:
        manager_user = ManagerHRManager.create_manager_user(db)
        return {"message": "Manager user created successfully", "user": manager_user.email}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Manager user: {str(e)}")
    

@router.get("/logout")
async def logout(response: Response):

    response.delete_cookie("access_token")

    return RedirectResponse(url="/login")