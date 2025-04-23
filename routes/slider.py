
from imports import *
import time
from AIServices.present import new_presentation, process_pdf
import logging


logging.getLogger("grpc").setLevel(logging.ERROR)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

api_key = os.getenv("GROQ_API")


@router.get("/slider", response_class=HTMLResponse)
async def slider_page(request: Request):
    return templates.TemplateResponse("employee/slider.html", {"request": request})

@router.post("/generate-presentation", response_class=JSONResponse)
def generate_presentation(
    request: Request,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
    template_name: str = Form(None)  
):
    """
    Handles PDF upload and generates a PowerPoint presentation.
    """
    try:
        # Authenticate User
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        token_data = decode_access_token(token.replace("Bearer ", ""))
        user_id = token_data.get("user_id")

        # Fetch user from database
        user = db.query(User).filter(User.user_id == user_id, User.is_deleted == 0).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Check file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")

        # Map template name to path
        template_path = "static/slides/Presentation2.pptx"  
        if template_name:
            if template_name.lower() == "present1":
                template_path = "static/slides/Presentation1.pptx"
            elif template_name.lower() == "present2":
                template_path = "static/slides/Presentation2.pptx"
            elif template_name.lower() == "present3":
                template_path = "static/slides/Presentation3.pptx"

        # Create user directory if it doesn't exist
        full_name = user.full_name
        user_directory = f"resources/{user_id}_{full_name}"
        os.makedirs(user_directory, exist_ok=True)
        
        # Save the uploaded PDF file
        timestamp = int(time.time())
        pdf_filename = f"{timestamp}_{file.filename}"
        pdf_path = os.path.join(user_directory, pdf_filename)
        
        # Save file
        file_content = file.file.read()
        with open(pdf_path, "wb") as f:
            f.write(file_content)
        
        # Create output path
        output_filename = f"{timestamp}_presentation.pptx"
        output_dir = "static/outputslider/"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)

        # Process the PDF and generate presentation
        try:
            result_path = new_presentation(pdf_path, api_key, template_path, output_path)
            
            # Record successful generation in log
            logging.info(f"Generated presentation at {result_path} from {pdf_path} using template {template_path}")
            
            return JSONResponse({
                "status": "success",
                "message": "Presentation generated successfully",
                "pdf_path": pdf_path,
                "template_path": template_path,
                "output_path": result_path
            })
            
        except Exception as e:
            logging.error(f"Error generating presentation: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to generate presentation: {str(e)}")
            
    except Exception as e:
        logging.error(f"Error in generate_presentation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
