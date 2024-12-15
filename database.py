from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, ForeignKey, func, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, mapped_column, Mapped
from typing import Optional
from datetime import datetime


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


    # One-to-many relationship with Post (a user can have many posts)
    posts = relationship("Post", back_populates="author")  

    # One-to-many relationship with Task (assigned to a user and assigned by a user)
    tasks_assigned_to = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    tasks_assigned_by = relationship("Task", foreign_keys="Task.assigned_by_id", back_populates="assigned_by")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, full_name='{self.full_name}', email='{self.email}')>"

class Task(Base):
    __tablename__ = "task"
    
    task_id: Mapped[str] = Column(String, primary_key=True,  nullable=False)
    title: Mapped[str] = Column(String(255), nullable=False)
    description: Mapped[Optional[str]] = Column(Text, nullable=True)
    due_date: Mapped[Optional[datetime]] = Column(Date, nullable=True)
    docs_path: Mapped[Optional[str]] = Column(String(255), nullable=True)
    status: Mapped[str] = Column(String(50), default="Pending", nullable=False)
    deleted_at: Mapped[Optional[datetime]] = Column(Date, nullable=True)  # Properly mapped

    # Foreign keys
    assigned_to_id: Mapped[Optional[str]] = Column(String(10), ForeignKey("user.user_id"), nullable=True)
    assigned_by_id: Mapped[Optional[str]] = Column(String(10), ForeignKey("user.user_id"), nullable=True)

    # Relationships with User
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="tasks_assigned_to")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id], back_populates="tasks_assigned_by")

    def __repr__(self) -> str:
        return (f"<Task(task_id={self.task_id}, title='{self.title}', "
                f"status='{self.status}', docs_path='{self.docs_path}')>")
    
# class Task(Base):
#     __tablename__ = "task"
    
#     task_id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
#     title = Column(String(255), nullable=False)
#     description = Column(Text, nullable=True)
#     due_date = Column(Date, nullable=True)
#     docs_path = Column(String(255), nullable=True)
#     status = Column(String(50), default="Pending", nullable=False)
#     deleted_at: Optional[datetime] = None 

#     # Foreign keys
#     assigned_to_id = Column(String(10), ForeignKey("user.user_id"), nullable=True)
#     assigned_by_id = Column(String(10), ForeignKey("user.user_id"), nullable=True)

#     # Relationships with User
#     assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="tasks_assigned_to")
#     assigned_by = relationship("User", foreign_keys=[assigned_by_id], back_populates="tasks_assigned_by")

#     def __repr__(self):
#         return (f"<Task(task_id={self.task_id}, title='{self.title}', "
#                 f"status='{self.status}', docs_path='{self.docs_path}')>")


class Post(Base):
    __tablename__ = "post"
    
    post_id = Column(String(20), primary_key=True, index=True)
    user_id = Column(String(10), ForeignKey("user.user_id"), nullable=False)
    department_name = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    created_date = Column(DateTime, default=func.now())

    # Relationship with User
    author = relationship("User", back_populates="posts")

    def __repr__(self):
        return f"<Post(post_id={self.post_id}, title='{self.title}', created_date='{self.created_date}')>"

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
