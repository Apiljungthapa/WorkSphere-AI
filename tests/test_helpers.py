# import sys
# import os
# import shutil
# from datetime import datetime
# from fastapi import HTTPException
# import pytest
# import pytz
# from unittest import mock
# # from ..models.database import get_db, User, Post, Like
# from sqlalchemy.orm import Session,sessionmaker
# # from utils.helpers import fetch_posts_for_user



# # Add parent directory to the path
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# def test_generate_initials():

#     from utils.helpers import generate_initials

#     assert generate_initials("Apil Thapa") == "AT"
    
#     # Test case with a single name
#     assert generate_initials("Ram") == "R"
    
#     # Test case with an empty string
#     assert generate_initials("") == ""
    
#     # Test case with a single initial
#     assert generate_initials("Mohan Karki") == "MK"
    
#     # Test case with no space
#     assert generate_initials("Alice") == "A"
    
#     # Test case with spaces in between
#     assert generate_initials("  Alice   Johnson  ") == "AJ"



# def test_generate_otp_code():
#     from utils.helpers import generate_otp_code
#     otp = generate_otp_code()
#     assert len(otp) == 6
#     assert otp.isdigit()



# def test_generate_task_id():
#     from utils.helpers import generate_task_id
#     task_id = generate_task_id()
#     assert task_id.startswith("TSK")
#     assert len(task_id) == 6

# def test_create_user_directory():
#     from utils.helpers import create_user_directory
#     user_id = "EMP001"
#     full_name = "Apil Thapa"
#     dir_path = create_user_directory(user_id, full_name)
#     assert dir_path.exists()
#     assert dir_path.is_dir()

#     # Cleanup
#     shutil.rmtree(dir_path)

# def test_convert_utc_to_nepal_local():
#     from utils.helpers import convert_utc_to_nepal_local
#     utc_now = datetime.utcnow()
#     nepal_time = convert_utc_to_nepal_local(utc_now)
#     assert nepal_time.tzinfo.zone == 'Asia/Kathmandu'


# # @pytest.fixture
# # def mock_db_session():
# #     # Mock the database session
# #     return mock.MagicMock(Session)

# # def test_fetch_posts_for_user(mock_db_session):
# #     # Sample user and post data
# #     user_id = "EMP001"
# #     user = User(user_id=user_id, department_name="Engineering", is_deleted=0, full_name="Apil Thapa")
# #     post = Post(post_id="PST001", user_id=user_id, created_date="2025-04-04", is_deleted=0)
# #     like = Like(user_id=user_id, post_id="PST001")

# #     # Mock `db.query(User)` to return a user
# #     mock_db_session.query.return_value.filter.return_value.first.return_value = user

# #     # Mock `db.query(Post)` to return a list of posts
# #     mock_db_session.query.return_value.join.return_value.filter.return_value.all.return_value = [post]

# #     # Mock `db.query(Like)` to check if the post is liked
# #     mock_db_session.query.return_value.filter.return_value.first.return_value = like

# #     # Mock `generate_initials` function to return a fixed value
# #     with mock.patch("your_module.generate_initials") as mock_generate_initials:
# #         mock_generate_initials.return_value = "AT"

# #         # Call the function
# #         posts = fetch_posts_for_user(user_id, mock_db_session)

# #         # Assertions
# #         assert len(posts) == 1  # We expect 1 post
# #         post = posts[0]
# #         assert post.is_liked is True  # Post is liked
# #         assert post.full_name == "Apil Thapa"
# #         assert post.initials == "AT"
# #         assert post.created_date == "April 04, 2025 12:00 AM"  # Assuming it was mocked to this format

# #         # Check if the mocked methods were called
# #         mock_db_session.query.return_value.filter.assert_called()
# #         mock_generate_initials.assert_called_with("Apil Thapa")

# # def test_user_not_found(mock_db_session):
# #     user_id = "NON_EXISTENT_USER"
    
# #     # Mock `db.query(User)` to return None, simulating a user not found
# #     mock_db_session.query.return_value.filter.return_value.first.return_value = None
    
# #     with pytest.raises(HTTPException):
# #         fetch_posts_for_user(user_id, mock_db_session)