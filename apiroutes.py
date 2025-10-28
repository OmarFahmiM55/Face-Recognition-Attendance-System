from fastapi import APIRouter, UploadFile, File, HTTPException, Form , Query
import cv2
import json
import numpy as np
import face_recognition
from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from tables import FaceEncoding
from faceFunctions import load_known_encodings, compare_faces , encode_face
from attendence import log_attendance
from camerasetup import start_camera_monitoring, get_camera_connection
from fastapi.responses import StreamingResponse
import time

router = APIRouter()


@router.post("/signup")
async def signup(
    file: UploadFile = File(...),
    user_id: str = Form(...)
):
    try:
        encoding, error_msg = encode_face(file.file)
        
        if error_msg:
            return {"error": error_msg}
        
        # Convert to list & JSON
        encoding_vector = encoding.tolist()
        json_encoding = json.dumps(encoding_vector)

        # Save to database
        db_connection = SessionLocal()
        try:
            existing_user = db_connection.query(FaceEncoding).filter(FaceEncoding.user_id == user_id).first()
            if existing_user:
                return {"error": f"User {user_id} already exists. Use a different user ID."}
            
            new_encoding = FaceEncoding(
                user_id=user_id,
                encoding=json_encoding,
                fingerprint_enabled=0
            )
            db_connection.add(new_encoding)
            db_connection.commit()
            db_connection.refresh(new_encoding)
            print(f"User {user_id} registered successfully")

        except SQLAlchemyError as e:
            db_connection.rollback()
            print(f"Database error: {str(e)}")
            return {"error": f"Database error: {str(e)}"}
        finally:
            db_connection.close()
        
        return {
            "message": "Face encoding saved successfully",
            "user_id": user_id
        }
    
    except Exception as e:
        print(f"Error in signup: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

    
    except Exception as e:
        print(f" Registration failed for user {user_id}: {str(e)}")
        return {"error": f"Registration failed: {str(e)}"}

@router.post("/start_monitoring")
async def start_monitoring():
    print("Starting the camera")
    result = start_camera_monitoring()
    return result


@router.get("/registered_users")
async def get_registered_users(user_id: str = Query(...)):
    db = SessionLocal()
    try:
        user = db.query(FaceEncoding).filter(FaceEncoding.user_id == user_id, FaceEncoding.fingerprint_enabled == 1).first()
        if user:
            return 1
        else:
            return 0

    except Exception as e:
        return {"error": f"ERROR: {str(e)}"}
    finally:
        db.close()