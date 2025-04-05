from fastapi import Request, HTTPException
from fastapi.responses import RedirectResponse
from imports import *
class AuthMiddleware(BaseHTTPMiddleware):
    MANAGER_PAGES = [
        "/register-employee",
        "/dash",
        "/assign-task",
        "/tracking.html",
        "/updateEmployee.html"
        "/update_policies",
        "/policy",
        
        
    ]

    EMPLOYEE_PAGES = [
        "/dashboard",
        "/feedback",
        "/view_notifications",
        "/profile",
        "/view_announcements",
        "/emp_details",
        "/assignment",
        "/employee-details",
        "/summary",
        "/rag",
        "/post/edit",
        "/check_unread_announcements",
        "/get_policy"
    ]

    EXEMPT_PAGES = ["/", "/login", "/check_email", "/ishDetails", "/ishPage", "/static", "/hr_check_password"]

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow static files and exempt pages to bypass authentication
        if path.startswith("/static/") or path in self.EXEMPT_PAGES:
            return await call_next(request)

        token = request.cookies.get("access_token")

        # If no token, redirect to login page
        if not token:
            if path != "/login":  # Allow access to the login page
                return RedirectResponse(url="/login")
            return await call_next(request)

        try:
            # Decode the token to get user data
            token_data = decode_access_token(token.replace("Bearer ", ""))
        except HTTPException:
            # If token is invalid or expired, redirect to login
            return RedirectResponse(url="/login")

        if not token_data:
            # If token data is empty, redirect to login
            return RedirectResponse(url="/login")

        role = token_data.get("role")

        if role is None:
            # If role is not defined, redirect to login
            return RedirectResponse(url="/login")

        # Get the last visited page from the referer header
        last_page = request.headers.get("referer", "/")

        # If user is already logged in and tries to access the login page, redirect to last visited page
        if path == "/login":
            # Ensure the last page is not an exempt page (e.g., "/login")
            if last_page not in self.EXEMPT_PAGES:
                return RedirectResponse(url=last_page)
            else:
                # Redirect to a default page based on role
                if role == "employee":
                    return RedirectResponse(url="/dashboard")
                elif role == "manager":
                    return RedirectResponse(url="/dash")

        # Check role-based access
        if role == "employee" and path in self.MANAGER_PAGES:
            return RedirectResponse(url=last_page if last_page in self.EMPLOYEE_PAGES else "/dashboard")

        if role == "manager" and path in self.EMPLOYEE_PAGES:
            return RedirectResponse(url=last_page if last_page in self.MANAGER_PAGES else "/dash")

        # Allow access to the requested page
        return await call_next(request)