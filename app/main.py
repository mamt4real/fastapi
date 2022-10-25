from fastapi import FastAPI
from .routers import users, posts, auth, votes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# database connection
# models.Base.metadata.create_all(bind=engine)


@app.get("/")
async def root():
    return {"message": "Hello message"}

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(posts.router)
app.include_router(votes.router)
