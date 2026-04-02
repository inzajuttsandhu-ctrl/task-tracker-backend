from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from bson import ObjectId
from database import tasks_collection, users_collection
from email_service import send_reminder_email
from apscheduler.schedulers.background import BackgroundScheduler
import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Task(BaseModel):
    title: str
    description: Optional[str] = ""
    dueDate: str
    priority: Optional[str] = "medium"
    status: Optional[str] = "pending"
    user_email: str

class User(BaseModel):
    name: str
    email: str
    password: str

def fix_id(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def check_deadlines():
    print("🔍 Checking deadlines...")
    tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    tasks = list(tasks_collection.find({"dueDate": tomorrow, "status": "pending"}))
    for task in tasks:
        send_reminder_email(task["user_email"], task["title"], task["dueDate"])
        print(f"📧 Reminder sent for: {task['title']}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_deadlines, "interval", hours=24, next_run_time=datetime.datetime.now())
scheduler.start()

@app.post("/signup")
def signup(user: User):
    existing = users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    users_collection.insert_one(user.dict())
    return {"message": "Account created successfully"}

@app.post("/login")
def login(user: User):
    found = users_collection.find_one({"email": user.email, "password": user.password})
    if not found:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"message": "Login successful", "name": found["name"], "email": found["email"]}

@app.post("/tasks")
def create_task(task: Task):
    result = tasks_collection.insert_one(task.dict())
    return {"message": "Task created", "id": str(result.inserted_id)}

@app.get("/tasks/{email}")
def get_tasks(email: str):
    tasks = list(tasks_collection.find({"user_email": email}))
    return [fix_id(t) for t in tasks]

@app.put("/tasks/{task_id}")
def update_task(task_id: str, task: Task):
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": task.dict()})
    return {"message": "Task updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    tasks_collection.delete_one({"_id": ObjectId(task_id)})
    return {"message": "Task deleted"}

@app.patch("/tasks/{task_id}/toggle")
def toggle_task(task_id: str):
    task = tasks_collection.find_one({"_id": ObjectId(task_id)})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    new_status = "completed" if task["status"] == "pending" else "pending"
    tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": {"status": new_status}})
    return {"message": "Status toggled", "status": new_status}

@app.get("/send-reminders")
def send_reminders():
    check_deadlines()
    return {"message": "Reminders checked and sent!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)