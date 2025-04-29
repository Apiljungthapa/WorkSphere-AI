
from imports import *

router = APIRouter()
templates = Jinja2Templates(directory="templates")

summarizer = DocumentSummarizer()


@router.get("/summary")
async def get_summary(request: Request, db: Session = Depends(get_db)):
    
    return templates.TemplateResponse("employee/summarize.html", {"request": request})

@router.post("/upload-file", response_class=HTMLResponse)
async def upload_file(request: Request, db: Session = Depends(get_db), file: UploadFile = File(...)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    # Fetch user from the database
    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == 0).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    full_name = user.full_name  

    # Create user-specific directory
    user_directory = f"resources/{user_id}_{full_name}"
    if not os.path.exists(user_directory):
        os.makedirs(user_directory)

    file_path = os.path.join(user_directory, file.filename)

    # Save the uploaded file to the directory
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return JSONResponse(content={"file_path": file_path, "user_id": user_id})


@router.get("/summarize", response_class=HTMLResponse)
async def summarize_text(request: Request, file_path: str = Query(...), db: Session = Depends(get_db)):
    # Verify user has access to this file
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")
    
    # Check if file belongs to user (file path should contain user_id)
    if f"/{user_id}_" not in file_path and not file_path.startswith(f"resources/{user_id}_"):
        raise HTTPException(status_code=403, detail="You don't have permission to access this file")
        
    file_path = Path(file_path)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    
    summary = await summarizer.summarize_document(str(file_path))
        
    return JSONResponse(content={"summary": summary, "user_id": user_id})