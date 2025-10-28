import face_recognition
import json
from tables import FaceEncoding
import numpy as np

def encode_face(image_file):
    try:    
        # Load image file into numpy array (RGB format)
        image = face_recognition.load_image_file(image_file)
        print("Image loaded successfully")
        
        # Find all face locations in the image
        face_locations = face_recognition.face_locations(image)
        
        if not face_locations:
            return None, "No face found in the image" 
        
        # Convert face locations into numerical encodings
        # else
        encodings = face_recognition.face_encodings(image, face_locations)
        print(f"Image encoding successfully")
        
        if not encodings:
            return None, "Face encoding failed"
        
        return encodings[0], None
    

    except Exception as e:
        print(f"Error: {str(e)}")
        return None, f"Encoding error: {str(e)}"

def load_known_encodings(db_connection):
    try:
        all_records = db_connection.query(FaceEncoding).all()       # read/get all_records 
        result = []         # empty list to store the [user_id , encoding_array]
        
        print(f" Loading {len(all_records)} face encodings from database...")
        
        for record in all_records:
            try:
                encoding_list = json.loads(record.encoding)                 # load the encoding as json type 
                encoding_array = np.array(encoding_list, dtype=np.float64)  # convert the encoding array back to numpy array
                result.append((record.user_id, encoding_array))             # append [user_id , encoding_arry] to the empty list
                print("Loaded...")
                return result

            except Exception as e:
                print(" ERROR ")
                continue
            
    except Exception as e:
        print(f" Error loading encodings from database: {e}")
        return []

def compare_faces(known_encodings_list, face_encoding_to_check, tolerance=0.6):
    print(f"Comparing face with tolerance: {tolerance}")
    for user_id, known_face_encoding in known_encodings_list:
        try:
            matches = face_recognition.compare_faces([known_face_encoding], face_encoding_to_check, tolerance=tolerance)
            if matches[0]:
                face_distance = face_recognition.face_distance([known_face_encoding], face_encoding_to_check)[0]
                print(f"MATCH FOUND!x1x1x1 User ID: {user_id} (Distance: {face_distance:.3f})")
                return user_id
        except Exception as e:
            print(f"Error comparing with user {user_id}: {e}")
            continue
    
    print("No match found")
    return None

