from imports import *

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_TRACE"] = ""

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(AuthMiddleware)


# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"], 
#     allow_credentials=True,
#     allow_methods=["*"],  
#     allow_headers=["*"], 
# )

app.include_router(auth.router)
app.include_router(Employeedashboard.router)
app.include_router(Managerdashboard.router)
app.include_router(taskmanagement.router)
app.include_router(postmanagement.router)
app.include_router(announcement.router)
app.include_router(chat.router)
app.include_router(feedback.router)
app.include_router(summary.router)
app.include_router(ragDocsQuery.router)
app.include_router(notifications.router)




