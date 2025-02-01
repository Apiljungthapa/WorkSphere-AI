from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, func, Boolean, UniqueConstraint,Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped
from typing import Optional
from datetime import datetime, timezone

# Database Configuration
DATABASE_URL = "mysql+pymysql://root:@localhost/EMS2"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    
    user_id = Column(String(10), primary_key=True, unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(15), nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=True)
    department_name = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    otp_code = Column(String(10), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    isannouncement_read = Column(String(10))  
    istask_read = Column(String(10))
    isnotificationread = Column(String(10))

    


    # One-to-many relationship with Post (a user can have many posts)
    posts = relationship("Post", back_populates="author")  
    likes = relationship("Like", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    support_feedbacks = relationship("SupportFeedback", back_populates="user")
    chatrooms_as_emp1 = relationship("Chatroom", foreign_keys="[Chatroom.emp1_id]",  back_populates="emp1", overlaps="emp1, emp2")
    chatrooms_as_emp2 = relationship("Chatroom", foreign_keys="[Chatroom.emp2_id]", back_populates="emp2", overlaps="emp1, emp2")
    announcement = relationship("Announcement", back_populates="manager")


    # One-to-many relationship with Task (assigned to a user and assigned by a user)
    tasks_assigned_to = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    tasks_assigned_by = relationship("Task", foreign_keys="Task.assigned_by_id", back_populates="assigned_by")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, full_name='{self.full_name}', email='{self.email}')>"

class Task(Base):
    __tablename__ = "task"
    
    task_id = Column(String, primary_key=True, nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(Date, nullable=True)
    docs_path = Column(String(255), nullable=True)
    status = Column(String(50), default="Pending", nullable=False)
    deleted_at = Column(Date, nullable=True)

    # Foreign keys
    assigned_to_id = Column(String(10), ForeignKey("user.user_id"), nullable=True)
    assigned_by_id = Column(String(10), ForeignKey("user.user_id"), nullable=True)

    # Relationships with User
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="tasks_assigned_to")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], back_populates="tasks_assigned_by")

    def __repr__(self) -> str:
        return f"<Task(task_id={self.task_id}, title='{self.title}', status='{self.status}')>"

class Post(Base):
    __tablename__ = "post"
    
    post_id = Column(String(50), primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_date = Column(DateTime, nullable=False)
    user_id = Column(String(50), ForeignKey("user.user_id"), nullable=True)
    deleted_at = Column(Integer, default=0)

    # Relationship with User
    author = relationship("User", back_populates="posts")
    likes_relation = relationship("Like", back_populates="post")
    comments = relationship("Comment", back_populates="post")

    def __repr__(self):
        return f"<Post(post_id={self.post_id}, title='{self.title}', created_date='{self.created_date}')>"

class Like(Base):
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("post.post_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(10), ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)

    # Ensure a user can like a post only once
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_post_user_like'),)

    # Relationships
    post = relationship("Post", back_populates="likes_relation")
    user = relationship("User", back_populates="likes")



class Comment(Base):
    __tablename__ = 'comment'  # Name of the table in the database

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)  # Content of the comment
    comment_date = Column(DateTime, nullable=False)  # Date and time of the comment
    post_id = Column(Integer, ForeignKey('post.post_id'), nullable=False)  # Foreign key to the Post table
    user_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)  # Foreign key to the User table

    # Relationships
    post = relationship('Post', back_populates='comments') 
    user = relationship('User', back_populates='comments')


class SupportFeedback(Base):
    __tablename__ = "support_feedback"

    feedback_id = Column(String(50), primary_key=True, nullable=False)  
    feedback_type = Column(String(50), nullable=False)  
    message = Column(Text, nullable=False)  
    user_id = Column(String(10), ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)  
    created_at = Column(DateTime, default=func.now(), nullable=False) 

    # Relationships
    user = relationship("User", back_populates="support_feedbacks")



class Chatroom(Base):
    __tablename__ = 'chatroom'

    chat_id = Column(String(10), primary_key=True)  # Unique chatroom ID
    created_date = Column(DateTime, default=datetime.utcnow)
    emp1_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)  # Employee 1 ID
    emp2_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)  # Employee 2 ID

    # # Relationships
    # # messages = relationship("ChatMessage", back_populates="chatroom")
    # emp1 = relationship("User", foreign_keys=[emp1_id])  # Employee 1 user relationship
    # emp2 = relationship("User", foreign_keys=[emp2_id])

    emp1 = relationship("User", foreign_keys=[emp1_id], back_populates="chatrooms_as_emp1", overlaps="chatrooms_as_emp1,chatrooms_as_emp2")  
    emp2 = relationship("User", foreign_keys=[emp2_id], back_populates="chatrooms_as_emp2", overlaps="chatrooms_as_emp1,chatrooms_as_emp2")



class Message(Base):
    __tablename__ = 'message'

    msg_id = Column(Integer, primary_key=True)
    content = Column(String, nullable=False)
    status = Column(String, default='sent')  # e.g., 'sent', 'delivered', 'read'
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    chat_id = Column(String(10), ForeignKey('chatroom.chat_id'), nullable=False)
    sender_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('user.user_id'), nullable=False)

    # Relationships
    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])


class Announcement(Base):
    __tablename__ = "announcement"

    announcement_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    date = Column(DateTime, nullable=False)
    content = Column(Text, nullable=False)
    priority_level = Column(String(50), nullable=False)
    manager_id = Column(Integer, ForeignKey("user.user_id"), nullable=False) 

    manager = relationship("User", back_populates="announcement")



class Notification(Base):
    __tablename__ = 'notification'
    
    notification_id = Column(String(255), primary_key=True)  
    content = Column(Text, nullable=False)                    
    date = Column(DateTime, default=func.now()) 
    user_id = Column(String(50), ForeignKey("user.user_id"), nullable=True) 
    task_id = Column(String(50), ForeignKey("task.task_id"), nullable=True)
    

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
