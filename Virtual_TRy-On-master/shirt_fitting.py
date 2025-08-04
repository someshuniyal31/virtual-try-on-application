import os
import cvzone
import cv2
from cvzone.PoseModule import PoseDetector
from rembg import remove
from PIL import Image
import numpy as np
import io

def remove_background(image_path, output_path):
    # Open the image and remove the background
    with open(image_path, "rb") as input_file:
        input_data = input_file.read()

    # Remove the background using rembg
    output_data = remove(input_data)

    # Convert to image (PIL)
    output_image = Image.open(io.BytesIO(output_data))

    # Convert to numpy array
    output_array = np.array(output_image)

    # Check for non-transparent pixels (alpha channel != 0)
    alpha_channel = output_array[:, :, 3]  # Alpha channel is in the 4th channel (index 3)
    mask = alpha_channel != 0  # This will create a mask where the body is

    # Extract the region of the body using the mask (using np.where to get body pixels)
    body_pixels = np.zeros_like(output_array)  # Empty black image
    body_pixels[mask] = output_array[mask]  # Copy body pixels

    # Convert back to Image
    body_image = Image.fromarray(body_pixels)

    # Save the body-only image
    body_image.save(output_path)

    return output_path

def apply_shirt_to_person(person_image_path, shirt_image_path, output_image_path):
    # First remove the background from the person's image
    temp_output_image_path = "static/uploads/temp_person_no_bg.png"
    remove_background(person_image_path, temp_output_image_path)

    # Load the person's image with background removed (this should only have the body)
    img = cv2.imread(temp_output_image_path, cv2.IMREAD_UNCHANGED)

    # Initialize PoseDetector to detect the person's pose
    detector = PoseDetector()

    fixedRatio = 294 / 202
    shirtRatioHeightWidth = 581 / 440  # From Shirt Dimensions

    # Detect person's pose
    img = detector.findPose(img, draw=False)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList:
        lm11 = lmList[11][0:2]  # Left shoulder
        lm12 = lmList[12][0:2]  # Right shoulder

        # Load the shirt image
        imgShirt = cv2.imread(shirt_image_path, cv2.IMREAD_UNCHANGED)

        # Calculate the width of the shirt based on the distance between shoulders
        widthOfShirt = int((lm11[0] - lm12[0]) * fixedRatio)
        imgShirt = cv2.resize(imgShirt, (widthOfShirt, int(widthOfShirt * shirtRatioHeightWidth)))

        # Calculate scale for the shirt
        currentScale = (lm11[0] - lm12[0]) / 202
        offset = int(50 * currentScale), int(50 * currentScale)

        try:
            # Overlay the shirt onto the person image (with no background)
            img = cvzone.overlayPNG(img, imgShirt, (lm12[0] - offset[0], lm12[1] - offset[1]))
        except Exception as e:
            print(f"Error overlaying shirt: {e}")
            pass

    # Save the final image with the shirt applied
    cv2.imwrite(output_image_path, img)

    return output_image_path
