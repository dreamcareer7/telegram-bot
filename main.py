from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from routers import creator, messaging, user, stripe, creator_data
from db.mongodb import db
app = FastAPI()

from firebase.firebase_app import getFirebaseApp

firebaseApp = getFirebaseApp()

# TODO: add specific origins here
origins = [ "*" ]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# Add routers to app
app.include_router(creator.router)
app.include_router(messaging.router)
app.include_router(user.router)
app.include_router(stripe.router)
app.include_router(creator_data.router)

# Root route
@app.get("/")
async def root():
    return {"message": "Hello World"}
