from fastapi import FastAPI,Request,Form,Depends
from fastapi.templating import Jinja2Templates
from  fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware 
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from sqlalchemy import Column,Integer,String,Boolean,DateTime
from datetime import datetime


Base=declarative_base()
engine=create_engine("sqlite:///todo.db")
SessionLocal=sessionmaker(bind=engine)
def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates=Jinja2Templates(directory="templates")
class Task(Base):
    __tablename__="todo"
    id=Column(Integer,primary_key=True)
    title=Column(String(90),nullable=False)
    description=Column(String(300))
    priority=Column(String(50),nullable=False)
    is_completed=Column(Boolean,default=False)
    created_by=Column(String(90),nullable=False)
    created_at=Column(DateTime,default=datetime.utcnow)

Base.metadata.create_all(engine)


app=FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="multiverse"
)

@app.get("/test-db")
def test_db():
    db=SessionLocal()
    todo=Task(
        title="Learn fastapi",
        description="Practise it",
        priority="High",
        is_completed=False,
        created_by="DHarmiksinh"
    )
    db.add(todo)
    db.commit()
    db.close()

    return {"Message":"Task Saved In the Database"}
@app.get("/")
def home(request:Request,db=Depends(get_db)):
    username=request.session.get("username")
    db=SessionLocal()

    tasks=db.query(Task).filter(Task.created_by == username).all()
    pending_task=db.query(Task).filter(Task.created_by ==username,Task.is_completed==False).all()
    complete_task=db.query(Task).filter(Task.created_by ==username,Task.is_completed==True).all()
    print(username)
    print(tasks)
    db.close()
    return templates.TemplateResponse(request,"index.html",{"pending_task":pending_task,"complete_task":complete_task})

@app.get("/login")
def login(request:Request):
    return templates.TemplateResponse(request,"login.html",{"request":request}) 

@app.post("/login")
def login(request:Request,username:str = Form(...)):
    print(username)
    request.session["username"]=username
    return {"message":"Login Successful"}

@app.post("/add")
def add(
        request:Request,
        title:str=Form(...),
        description:str=Form(...),
        priority:str=Form(...),db=Depends(get_db)):


    task=Task(
        title=title,
        created_by=request.session.get("username"),
        description=description,
        priority=priority
    )
    db.add(task)
    db.commit()
    db.close()
    return RedirectResponse("/",status_code=303)
@app.get("/toggle/{id}")
def toggle(id:int,db=Depends(get_db)):
    task=db.query(Task).filter(Task.id==id).first() 
    task.is_completed=not task.is_completed

    db.commit()
    return RedirectResponse("/",status_code=303)
