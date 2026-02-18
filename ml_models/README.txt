Place your trained MobileNetV2 model here.

Filename must be: mobilenetv2_pneumonia_model.h5

Model requirements:
- Format: Keras .h5 file
- Input: 224x224x1 (grayscale images)
- Output: Single value (0-1)
  - < 0.5 = NORMAL
  - >= 0.5 = PNEUMONIA
