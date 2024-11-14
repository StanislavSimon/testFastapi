from fastapi import FastAPI, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()
templates = Jinja2Templates(directory="templates")

DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    is_completed = Column(Boolean, default=False)


Base.metadata.create_all(bind=engine)


class TaskCreate(BaseModel):
    text: str


@app.get("/", response_class=HTMLResponse)
async def read_tasks(request: Request):
    db: Session = SessionLocal()
    tasks = db.query(Task).all()
    return templates.TemplateResponse("task_list.html", {"request": request, "tasks": tasks})


@app.post("/add")
async def add_task(text: str = Form(...)):
    db: Session = SessionLocal()
    new_task = Task(text=text)
    db.add(new_task)
    db.commit()
    return {"message": "Task added"}


@app.post("/delete/{task_id}")
async def delete_task(task_id: int):
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        db.delete(task)
        db.commit()
        return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/complete/{task_id}")
async def complete_task(task_id: int):
    db: Session = SessionLocal()
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.is_completed = not task.is_completed
        db.commit()
        return {"message": "Task status updated"}
    raise HTTPException(status_code=404, detail="Task not found")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
