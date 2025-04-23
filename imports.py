from fastapi import FastAPI, Form, Depends, Request, HTTPException, Query, UploadFile, File, Response, WebSocketDisconnect, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session,sessionmaker
from models.database import get_db, User,  Post, Like,Task, Comment, SupportFeedback, Chatroom, Message, Announcement, Notification, ChatHistory, CompanyPolicy
from fastapi.security import OAuth2PasswordBearer
import random
import random
import string
from collections import defaultdict
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import uuid
from pathlib import Path
import os
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import SQLAlchemyError
from fastapi.websockets import WebSocket
from typing import Dict, List
from utils.helpers import generate_initials, convert_utc_to_nepal_local, generate_unique_user_id, generate_task_id, create_user_directory, fetch_comments_for_posts,fetch_posts_for_user ,generate_otp_code, Hasher, ManagerHRManager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.security import create_access_token, decode_access_token
from AIServices.sentiment import SentimentAnalyzer
from AIServices.summarizer import DocumentSummarizer
from AIServices.rag import process_pdf_query,RAGSystem
from routes import auth, Employeedashboard, Managerdashboard, taskmanagement, postmanagement, announcement, chat, feedback, summary, notifications, ragDocsQuery
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.staticfiles import StaticFiles
import pytz
import json
from middlewares.auth_middleware import AuthMiddleware 
from starlette.middleware.base import BaseHTTPMiddleware
from dotenv import load_dotenv
import asyncio
from pydantic import BaseModel, Field
from typing import List, Optional, Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_AUTO_SIZE, PP_ALIGN
import re
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate

import logging
logging.getLogger("grpc").setLevel(logging.ERROR)

