from imports import *
import pytz

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/feed", response_class=HTMLResponse)
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


    users = db.query(User.user_id, User.full_name).filter(
    User.user_id != logged_in_user_id,
    User.is_deleted == 0 
).all()

    

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
        "employee/feed.html",
        {
            "request": request,
            "users": users_with_initials,
            "logged_in_user_id": logged_in_user_id,
            "back_url": back_url 
        }
    )



@router.get("/chatting")
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
    
    # Check if a chatroom exists between emp1 and emp2
    chatroom = (
    db.query(Chatroom)
    .filter(
        ((Chatroom.emp1_id == emp1_id) & (Chatroom.emp2_id == emp2_id)) |
        ((Chatroom.emp1_id == emp2_id) & (Chatroom.emp2_id == emp1_id)),
        Chatroom.is_deleted == 0  
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
        "employee/chatting.html",
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


@router.get("/total_unread")
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
@router.websocket("/ws/{user_id}")
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
@router.get("/chats/{chat_id}")
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