# Face Recognition Attendance System

Real-time employee attendance using **face recognition**, **FastAPI**, **OpenCV**, and **MySQL**.

---

## Features
- Register employees via image upload (`/api/signup`)
- Real-time face detection from RTSP camera
- Automatic attendance logging (no duplicates)
- Prevents double check-ins
- REST API with FastAPI

---

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy
- **CV**: `face_recognition` (dlib), OpenCV
- **Database**: MySQL
- **Streaming**: RTSP camera
- **Security**: Environment variables (`.env`)

