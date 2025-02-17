from django.shortcuts import render, redirect
from django.http import HttpResponse, StreamingHttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
import cv2 as cv
import face_recognition
import numpy as np
import dlib
from .models import PostImage

# Load dlib's pre-trained face detector and shape predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
face_rec_model = dlib.face_recognition_model_v1('dlib_face_recognition_resnet_model_v1.dat')

# Known face encodings and their labels
known_faces = []  # List to hold encodings of known faces
known_names = ['Aditya_Shelar','Pranav_Shewale','Ayush_Salunke']  # Labels corresponding to each face

# Load images and encode faces
aditya_image = face_recognition.load_image_file("Images/aditya.jpg")
pranav_image = face_recognition.load_image_file("Images/pranav.jpeg")

# Encode the faces and add them to the known_faces list
aditya_encoding = face_recognition.face_encodings(aditya_image)[0]
pranav_encoding = face_recognition.face_encodings(pranav_image)[0]

known_faces = [aditya_encoding, pranav_encoding]

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmation = request.POST['confirmation']

        if password == confirmation:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already used')
                return redirect('register')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already Taken')
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                messages.info(request, 'user created successfully')
                return redirect('login')
        else:
            messages.info(request, 'password not matching')
            return redirect('register')
    else:
        return render(request, 'register.html')

def login(request):
    if(request.method == 'POST'):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(username=username, email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Wrong credentials entered')
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def video_capture(request):
    return render(request, 'video_capture.html')

# Improved video streaming function with face detection and alignment
def gen():
    video = cv.VideoCapture(0)
    if not video.isOpened():
        print("Error: Could not open webcam.")
        return

    while True:
        isTrue, frame = video.read()
        if not isTrue or frame is None:
            print("Error: Failed to grab frame")
            break

        # Convert the frame to grayscale for face detection (optional)
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # Detect faces using dlib
        faces = detector(frame)

        for face in faces:
            x, y, w, h = (face.left(), face.top(), face.width(), face.height())
            
            # Draw a rectangle around the face
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Get facial landmarks
            landmarks = predictor(frame, face)

            # Get the face encoding using dlib's face recognition model
            face_encoding_dlib = face_rec_model.compute_face_descriptor(frame, landmarks)

            # Convert the Dlib encoding to a numpy array
            face_encoding = np.array(face_encoding_dlib)

            # Compare with known faces using face_recognition
            matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.4)  # Lower tolerance for more accuracy

            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]

            # Draw the label with the name on the frame
            cv.putText(frame, name, (x, y - 10), cv.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the resulting frame
        cv.imshow("Face Recognition", frame)

        # Press 'd' to quit the loop
        if cv.waitKey(20) & 0xFF == ord('d'):
            break

    video.release()
    cv.destroyAllWindows()

# Streaming the video feed
def video_feed(request):
    return StreamingHttpResponse(gen(), content_type='multipart/x-mixed-replace; boundary=frame')

def upload_image(request):
    if request.method == 'POST':
        if 'image' in request.FILES:
            image = request.FILES['image']
            # Assuming you have an Image model with a field 'image'
            new_image = PostImage(image=image)
            new_image.save()
            # Load the uploaded image and encode the face
            uploaded_image = face_recognition.load_image_file(new_image.image.path)
            uploaded_encoding = face_recognition.face_encodings(uploaded_image)[0]

            # Add the new encoding to the known faces list
            known_faces.append(uploaded_encoding)
            known_names.append(request.POST['name'])  # Assuming you have a field 'name' in your form
            messages.info(request, 'Image uploaded successfully')
            return redirect('index')
        else:
            messages.info(request, 'No image uploaded')
            return redirect('upload_image')
    else:
        return render(request, 'upload_image.html')    
