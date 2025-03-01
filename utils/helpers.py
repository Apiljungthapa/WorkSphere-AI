from imports import *
import pytz 
from passlib.context import CryptContext

BASE_DIR = Path("resources")

SECRET_KEY = os.getenv("SECRET_KEY", "123##@!%#")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def generate_initials(full_name: str) -> str:
  
    name_parts = full_name.split()

    # Get the first letter of the first name
    first_name_initial = name_parts[0][0].upper()

    # Get the first three letters of the last name (if available)
    last_name_initial = name_parts[1][:1].upper() if len(name_parts) > 1 else ""

    return first_name_initial + last_name_initial



nepal_tz = pytz.timezone("Asia/Kathmandu")

# Convert UTC time to Nepal's local time (Asia/Kathmandu)
def convert_utc_to_nepal_local(utc_dt):
    """ Convert UTC datetime to Nepal's local time (NPT) """
    utc_dt = utc_dt.replace(tzinfo=pytz.utc)  # Make sure it's timezone-aware
    nepal_local_time = utc_dt.astimezone(nepal_tz)  # Convert to Nepal's time zone
    return nepal_local_time


def generate_otp_code() -> str:
    return ''.join(random.choices(string.digits, k=6))


def generate_unique_user_id(role: str, db: Session) -> str:
    """Generates a unique user ID based on role (MGR for manager, EMP for employee)."""
    prefix = "MGR" if role == "manager" else "EMP"

    last_user = db.query(User).filter(User.role == role).order_by(User.user_id.desc()).first()
    if last_user and last_user.user_id.startswith(prefix):
        last_id_num = int(last_user.user_id[len(prefix):])
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1

    return f"{prefix}{new_id_num:03}"

def generate_task_id():
    prefix = "TSK"
    unique_id = ''.join(random.choices(string.digits, k=3))  
    return f"{prefix}{unique_id}"



def create_user_directory(user_id: str, full_name: str) -> Path:
    """
    Creates a directory for the user if it does not exist.
    Folder name is based on user_id and full_name.
    """
    user_dir = BASE_DIR / f"{user_id}_{full_name.replace(' ', '_')}"
    user_dir.mkdir(parents=True, exist_ok=True)
    print("new ho",user_dir)
    return user_dir


def fetch_posts_for_user(user_id: str, db: Session) -> list:
    """
    Fetch posts for a user based on their department, excluding soft deleted posts, and including like status.
    Also fetches the created_date formatted to "YYYY-MM-DD HH:MM:SS".
    """
    # Fetch the user from the database
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get the user's department
    current_user_department = user.department_name

    posts = db.query(Post).join(User).filter(
        User.department_name == current_user_department,
        Post.is_deleted  == 0,
        User.is_deleted == 0,
    ).all()


    for post in posts:

        is_liked = db.query(Like).filter(Like.user_id == user_id, Like.post_id == post.post_id).first() is not None
        post.is_liked = is_liked
        author = db.query(User).filter(User.user_id == post.user_id).first()
        full_name = author.full_name if author else "Unknown"
        initials = generate_initials(full_name)

        if post.created_date:
            post.created_date = post.created_date.strftime("%B %d, %Y %I:%M %p")

        post.full_name = full_name
        post.initials = initials

    return posts


def fetch_comments_for_posts(posts: list, db: Session) -> dict:
    
    post_ids = [post.post_id for post in posts]
    comments = (
        db.query(Comment, User.full_name)
        .join(User, User.user_id == Comment.user_id)
        .filter(Comment.post_id.in_(post_ids), Comment.is_deleted == 0)
        .all()
    )

    # Organize comments by post_id
    comments_by_post = {}
    for comment, full_name in comments:
        initials = generate_initials(full_name)
        if comment.post_id not in comments_by_post:
            comments_by_post[comment.post_id] = []
        comments_by_post[comment.post_id].append(
            {
                "content": comment.content,
                "full_name": full_name,
                "initials": initials,
                "comment_date": comment.comment_date.strftime("%B %d, %Y %I:%M %p"),
            }
        )
    return comments_by_post


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class Hasher():
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
    


class ManagerHRManager:

    HR_EMAIL = "workspherehr@gmail.com"
    HR_PASSWORD = "hrpassword"  
    MANAGER_EMAIL = "workspheremanager@gmail.com"
    MANAGER_PASSWORD = "managerpassword"  

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)


    @staticmethod
    def create_hr_user(db: Session) -> User:

        hr_user = db.query(User).filter(User.email == ManagerHRManager.HR_EMAIL).first()
        if hr_user:
            return hr_user  
        else:
            hashed_password = ManagerHRManager.get_password_hash(ManagerHRManager.HR_PASSWORD)
            new_hr_user = User(
                user_id="HR002",
                email=ManagerHRManager.HR_EMAIL,
                password=hashed_password,
                role="HR",
                full_name="Worksphere HR",
                is_deleted=0,
                otp_code="634215"
            )

            db.add(new_hr_user)
            db.commit()
            db.refresh(new_hr_user)
            return new_hr_user

    @staticmethod
    def create_manager_user(db: Session) -> User:

        manager_user = db.query(User).filter(User.email == ManagerHRManager.MANAGER_EMAIL).first()
        if manager_user:
            return manager_user 
        else:
            hashed_password = ManagerHRManager.get_password_hash(ManagerHRManager.MANAGER_PASSWORD)
            new_manager_user = User(
                user_id="MGR002",
                email=ManagerHRManager.MANAGER_EMAIL,
                password=hashed_password,
                role="manager",
                full_name="Worksphere Manager",
                is_deleted=0,
                otp_code="123456"
            )
            db.add(new_manager_user)
            db.commit()
            db.refresh(new_manager_user)
            return new_manager_user
