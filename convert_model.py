import joblib
import numpy as np
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Load existing Scikit-Learn model
model = joblib.load("antivirus_ai_model.pkl")

# Define input shape (5 features used in our original dataset)
initial_type = [('float_input', FloatTensorType([None, 5]))]

# Convert to ONNX format
onnx_model = convert_sklearn(model, initial_types=initial_type)

# Save the converted model
with open("antivirus_ai_model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("✅ SUCCESS: AI Model converted to Android-compatible 'antivirus_ai_model.onnx'!")
