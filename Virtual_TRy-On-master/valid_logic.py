import cv2
import mediapipe as mp

def check_human_pose_with_hands(image_path):
    # Load Mediapipe Pose solution
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found!")
        return False

    # Convert the image to RGB (required by Mediapipe)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image for pose estimation
    results = pose.process(image_rgb)

    # Check if any pose landmarks are detected
    if not results.pose_landmarks:
        print("No human detected!")
        return False

    # Extract landmarks
    landmarks = results.pose_landmarks.landmark

    # Define key landmarks for arms, legs, and body alignment
    left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
    left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW] 
    right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
    left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE]
    right_ankle = landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE]
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE]
    right_knee = landmarks[mp_pose.PoseLandmark.RIGHT_KNEE]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    
    # Check hands position: hands should be down
    hands = (
        left_wrist.y > left_shoulder.y and
        right_wrist.y > right_shoulder.y and
        abs(left_wrist.x - left_shoulder.x) < 0.1 and  # Hands close to body
        abs(right_wrist.x - right_shoulder.x) < 0.1 and
        left_wrist.x > left_shoulder.x and 
        right_wrist.x < right_shoulder.x
    )

    # Check if standing straight: y-coordinates of ankles, knees, hips, and shoulders in ascending order
    standing_straight = (
        left_ankle.y > left_knee.y > left_hip.y > left_shoulder.y and
        right_ankle.y > right_knee.y > right_hip.y > right_shoulder.y
    )

    # Check full body or above-knees visibility
    body_visibility = (
        (left_ankle.visibility > 0.5 and right_ankle.visibility > 0.5) or
        (left_knee.visibility > 0.5 and right_knee.visibility > 0.5)
    )

    # Evaluate all conditions
    if hands and standing_straight and body_visibility:
        return True  # Pose is valid
    else:
        return False  # Pose is invalid