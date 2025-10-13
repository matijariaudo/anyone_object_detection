from yolo import predict_yolo

"""
Simple test script for the YOLO model prediction function.

This script imports the `predict_yolo` function from the YOLO module
and runs a prediction on a sample image (`camera.png`), then prints
the prediction results to the console.
"""

# Run prediction on a sample image
prediction = predict_yolo("./models/camera.png")

# Display results
print(prediction)
