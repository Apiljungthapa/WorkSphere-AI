import pytest
import requests
import os

ENDPOINT = "http://127.0.0.1:8000"

# def test_login_password():
#     payload = {
#         "email": "roshnithapaa@gmail.com",
#         "password": "wrongpassword",     
#         "otp_code": "099882"
#     }

#     response = requests.post(ENDPOINT + "/login", data=payload)

#     assert response.status_code == 200 or response.status_code == 401
#     assert "Incorrect password employee" in response.text


# def test_save_employee():
#     payload = {
#         "fullname": "Roshan Thapa",
#         "email": "roshnithapaa@gmail.com",
#         "phone": "9812345678",
#         "position": "Software Engineer",
#         "department": "Engineering",
#         "password": "securepass123"
#     }

#     response = requests.post(ENDPOINT + "/save-employee", data=payload, allow_redirects=False)

#     print("Status Code:", response.status_code)
#     print("Response Text:", response.text)

#     assert response.status_code in [200, 201, 303]

# def test_login_pin():
#     payload = {
#         "email": "roshnithapaa@gmail.com",
#         "password": "roshni123",     
#         "otp_code": "123456" 
#     }

#     response = requests.post(ENDPOINT + "/login", data=payload)

#     assert response.status_code == 200 or response.status_code == 401
#     assert "Incorrect OTP" in response.text




# BASE_URL = "http://127.0.0.1:8000"


# def test_submit_feedback(jwt_token):
#     url = f"{BASE_URL}/submit-feedback"
    
#     payload = {
#         "feedbackType": "Appreciation",
#         "message": "Great support and smooth user experience!"
#     }

#     headers = {
#         "Cookie": f"access_token={jwt_token}"
#     }

#     response = requests.post(url, data=payload, headers=headers)

#     assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
#     assert "Feedback submitted successfully" in response.text