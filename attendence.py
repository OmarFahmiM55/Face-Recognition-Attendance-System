from tables import FaceEncoding
from database import SessionLocal
from datetime import datetime
import sqlalchemy.exc



# takes a (user_id) parameter and logs their attendance
def log_attendance(user_id):
    with SessionLocal() as db:          # with --> Automatic cleanup , when the block ends the session is automatically closed
        try:
            # Check if user has already checked in
            latest_log = db.query(FaceEncoding).filter(FaceEncoding.user_id == user_id).order_by(FaceEncoding.detected_at.desc()).first()
            if latest_log.fingerprint_enabled == True:
                print(f"⏸ User {user_id} already checked in with fingerprint_enabled=True")
                return False

            latest_log.detected_at= datetime.now()
            latest_log.fingerprint_enabled = True
            db.commit()

            print(f" Attendance logged for User {user_id} with fingerprint_enabled=True")
            return True
        
        except sqlalchemy.exc.DatabaseError as e:
            db.rollback()
            print(f"Error logging attendance for User {user_id}: {e}")
            return False