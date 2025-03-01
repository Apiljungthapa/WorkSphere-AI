from imports import *


class AuthMiddleware(BaseHTTPMiddleware):
    MANAGER_PAGES = [
        "/register-employee",
        "/dash",
        "/assign-task",
        "/tracking.html",
        "/updateEmployee.html"
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
        "/check_unread_announcements"
    ]

    EXEMPT_PAGES = ["/", "/login", "/check_email", "/ishDetails", "/ishPage"]

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path  # Get full request path

        if path in self.EXEMPT_PAGES:
            return await call_next(request)

        token = request.cookies.get("access_token")

        # ✅ Redirect to login if no token exists
        if not token:
            if path != "/login":  # Allow access to /login when not logged in
                return RedirectResponse(url="/login")
            return await call_next(request)

        # ✅ Handle invalid token safely
        try:
            token_data = decode_access_token(token.replace("Bearer ", ""))
        except HTTPException:  # Catch invalid token error
            return RedirectResponse(url="/login")

        if not token_data:
            return RedirectResponse(url="/login")

        role = token_data.get("role")

        if role is None:
            return RedirectResponse(url="/login")

        last_page = request.headers.get("referer", "/")  # Get the last visited page

        # ✅ Prevent logged-in users from accessing /login → Redirect them back to where they were

        print("ayo hai dada",last_page)
        print("ayo hai dada",path)

        if path == "/login":
            return RedirectResponse(url=last_page if last_page not in self.EXEMPT_PAGES else "/dashboard")

        if role == "employee" and path in self.MANAGER_PAGES:
            return RedirectResponse(url=last_page if last_page in self.EMPLOYEE_PAGES else "/dashboard")

        # ✅ Redirect manager to last valid page if trying to access employee pages
        if role == "manager" and path in self.EMPLOYEE_PAGES:
            return RedirectResponse(url=last_page if last_page in self.MANAGER_PAGES else "/dash")

        return await call_next(request)