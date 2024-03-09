import torch
from torchvision import transforms
from torchvision.models import resnet50, ResNet50_Weights
from PIL import Image
import os
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="PIL.TiffImagePlugin")
# 模型路径
model_path = 'cat_dog_classifier_epoch70.pth'

# 加载模型
model_weights = ResNet50_Weights.DEFAULT
model = resnet50(weights=model_weights)

# 修改最后一个全连接层以适应二分类任务
num_ftrs = model.fc.in_features
model.fc = torch.nn.Linear(num_ftrs, 2)

# 加载模型状态字典，确保映射到CPU
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
model.eval()

# 图像转换
transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def predict_image(image_path):
    image = Image.open(image_path).convert('RGB')
    image = transform(image).unsqueeze(0)  # 添加一个批次维度

    with torch.no_grad():
        outputs = model(image)
        _, predicted = torch.max(outputs, 1)
        probabilities = torch.softmax(outputs, dim=1)

    # 打印图片名和预测概率
    print(
        f'{image_path}: 猫的概率为 {probabilities[0][0].item() * 100:.0f}%; 狗的概率为 {probabilities[0][1].item() * 100:.0f}%')


# 遍历petimages文件夹
for pet_class in ['dog', 'cat']:
    folder_path = os.path.join('petimages', pet_class)
    for image_name in os.listdir(folder_path):
        if image_name.lower().endswith(('png', 'jpg', 'jpeg')):
            image_path = os.path.join(folder_path, image_name)
            predict_image(image_path)
