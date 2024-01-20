# Global dependencies for FastAPI routes

from typing import Optional
from fastapi import FastAPI, Header, HTTPException, Depends
import firebase_admin
from firebase_admin import auth, credentials

# Load Firebase project credentials
cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

# Define the access token validation function
async def validate_access_token(access_token: Optional[str] = Header(None)):
    if access_token is None:
        raise HTTPException(status_code=401, detail="Access token missing")
    try:
        decoded_token = auth.verify_id_token(access_token)
        # You can pass the decoded token object to the route function or 
        # save it to the request state with `Depends()` if you want to use it later

        return decoded_token
    except auth.InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid access token")
