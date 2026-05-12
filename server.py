from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Optional
from sqlmodel import SQLModel, Session, create_engine, Field, select
from contextlib import asynccontextmanager
import uvicorn

sqlite_url = 'sqlite:///database.db'
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

class Store(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def show_main(request: Request):
    with Session(engine) as session:
        results = session.exec(select(Store)).all()
    
    return templates.TemplateResponse(
        request=request,
        name='login.html',
        context={'links': results}
    )

@app.post('/add-link')
async def add_link(title: str = Form(...), link: str = Form(...)):
    with Session(engine) as session:
        new_item = Store(title=title, link=link)
        session.add(new_item)
        session.commit()
    return RedirectResponse(url="/", status_code=303)

@app.post('/delete/{item_id}')
async def delete_link(item_id: int):
    with Session(engine) as session:
        item = session.get(Store, item_id)
        if item:
            session.delete(item)
            session.commit()
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
