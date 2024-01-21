import torch
import model.transfer_style as ts
import time
from config_data.config import Config, load_config
import requests
import io
from PIL import Image
import os

class StyleTransfer():
    config: Config = load_config()
    uri_info = f"https://api.telegram.org/bot{config.tg_bot.token}/getFile?file_id="
    uri = f"https://api.telegram.org/file/bot{config.tg_bot.token}/"

    def __init__(self):
        pass

    @staticmethod
    def take_pil_image(file_id:int) -> Image:
        uri = StyleTransfer.uri_info + file_id
        resp = requests.get(uri)
        img_path = resp.json()['result']['file_path']
        img = requests.get(StyleTransfer.uri + img_path)
        img = Image.open(io.BytesIO(img.content))
        return img
    
    @staticmethod
    def inference(content: Image, style: Image) -> Image:
        imsize = 512
        size_image = ts.calc_size(content, imsize=imsize)

        content_img = ts.image_loader(content,
                                    size_image=size_image)
        style_img = ts.image_loader(style,
                                    size_image=size_image)

        assert style_img.size() == content_img.size(), \
        "we need to import style and content images of the same size"

        cnn_normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(ts.device)
        cnn_normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(ts.device)

        cnn = torch.load('model/cnn.pth').to(ts.device)

        input_img = content_img.clone()
        output = ts.run_style_transfer(cnn,
                                cnn_normalization_mean,
                                cnn_normalization_std,
                                content_img,
                                style_img,
                                input_img,
                                style_weight=500000,
                                num_steps=300)

        return ts.from_tensor_to_pil_image(output)
    
    def __call__(self, content: int, path_to_style: str) -> Image:
        content_image = StyleTransfer.take_pil_image(content.file_id)
        style_image = Image.open(path_to_style)
        return StyleTransfer.inference(content_image, style_image)
    
model = StyleTransfer()


