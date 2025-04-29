from imports import *
import pytz
import asyncio
import logging 

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/rag")
async def generate_rag(request: Request, db: Session = Depends(get_db)):  
    return templates.TemplateResponse("employee/rag.html", {"request": request})

@router.post("/upload-rag-file", response_class=JSONResponse)
async def upload_rag_file(
    request: Request,
    db: Session = Depends(get_db),
    file: UploadFile = File(None),  # Optional file (can be None)
    question: str = Form(...),
    file_path: str = Form(None)  # Store file path for reuse
):
    """Handles file upload & allows subsequent queries without re-uploading the file."""
    try:
        # Authenticate User
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        token_data = decode_access_token(token.replace("Bearer ", ""))
        user_id = token_data.get("user_id")

        # Fetch user from database - make it non-blocking
        user = await asyncio.to_thread(
            lambda: db.query(User).filter(User.user_id == user_id, User.is_deleted == 0).first()
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # If a new file is uploaded, save it
        if file:
            full_name = user.full_name
            user_directory = f"resources/{user_id}_{full_name}"
            os.makedirs(user_directory, exist_ok=True)
            file_path = os.path.join(user_directory, file.filename)

            # Save file asynchronously
            file_content = await file.read()
            await asyncio.to_thread(lambda: open(file_path, "wb").write(file_content))

        # Ensure file_path exists (either from previous upload or current request)
        if not file_path:
            raise HTTPException(status_code=400, detail="No file provided and no existing file found.")
        
        # Get Nepal time
        utc_time = datetime.now(pytz.utc)
        nepal_time = convert_utc_to_nepal_local(utc_time)

        # Process the PDF query using the async function
        ai_response = await process_pdf_query(file_path, question) 

        # Format the response
        if hasattr(ai_response, "content"):
            ai_response = ai_response.content
        else:
            ai_response = str(ai_response)

        # Create and save chat history entry asynchronously
        new_chat_entry = ChatHistory(
            user_query=question,
            response=ai_response,
            user_id=user_id,
            timestamp=nepal_time,
            filepath=file_path  
        )
        
        # Make database operations non-blocking
        await asyncio.to_thread(lambda: db.add(new_chat_entry))
        await asyncio.to_thread(lambda: db.commit())
        
        # Fetch chat history in a non-blocking way
        chat_history = await asyncio.to_thread(
            lambda: db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id, ChatHistory.filepath == file_path)
            .order_by(ChatHistory.id.asc())
            .all()
        )

        history_data = [{"question": chat.user_query, "response": chat.response} for chat in chat_history]

        return JSONResponse({
            "file_path": file_path,
            "user_query": question,
            "ai_response": ai_response,
            "chat_history": history_data
        })
    
    except Exception as e:
        # Roll back transaction in case of error - make it non-blocking
        await asyncio.to_thread(lambda: db.rollback())
        # Log the error for debugging
        logging.error(f"Error in upload_rag_file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")