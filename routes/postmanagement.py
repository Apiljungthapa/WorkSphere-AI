from imports import *
import pytz # type: ignore

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/editpost", response_class=HTMLResponse)
async def post_edit_page(request: Request):
    return templates.TemplateResponse("employee/post_edit.html", {"request": request})


@router.post("/posts/")
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
        db.rollback()
        response = RedirectResponse(url="/emp_details", status_code=303)
        response.set_cookie("message", "Failed to create the post!")
        response.set_cookie("message_type", "error")
        return response
    
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


# post edit garda id pathaune  
@router.get("/post/edit/{post_id}", response_class=HTMLResponse)
async def post_edit_page(post_id: str, request: Request, db: Session = Depends(get_db)):

    post = db.query(Post).filter(Post.post_id == post_id).first()
    

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return templates.TemplateResponse(
        "employee/post_edit.html",
        {
            "request": request,
            "post": post,  
        },
    )


# post update garne code
@router.post("/edit_post/{post_id}", response_class=HTMLResponse)
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



@router.get("/post/delete/{post_id}", response_class=RedirectResponse)
async def soft_delete_post(post_id: str, request: Request, db: Session = Depends(get_db)):

    try:
        post = db.query(Post).filter(Post.post_id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post.is_deleted = 1  
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

@router.post("/post/{action}/{post_id}")
def toggle_like(action: str, post_id: str, request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token_data = decode_access_token(token.replace("Bearer ", ""))
    user_id = token_data.get("user_id")

    user = db.query(User).filter(User.user_id == user_id, User.is_deleted == 0).first()
    if not user:
        raise HTTPException(status_code=403, detail="User is deleted or not found")

    post = db.query(Post).filter(Post.post_id == post_id, Post.is_deleted == 0).first()
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
@router.post("/comments/")
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





