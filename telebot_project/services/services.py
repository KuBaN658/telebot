import torch
import model.transfer_style as ts
from torchvision import models
import time
from config_data.config import Config, load_config
import requests
import io
from PIL import Image, ImageFilter
import os



config: Config = load_config()
URI_INFO = f"https://api.telegram.org/bot{config.tg_bot.token}/getFile?file_id="
URI = f"https://api.telegram.org/file/bot{config.tg_bot.token}/"


def is_second(user_id: int, data: dict) -> bool:
    if user_id in data:
        return True
    return False


def add_photo(user_id: int, photo:list, data:dict, is_second: bool) -> None:
    file_id = photo[-1].file_id
    if is_second:
        content = take_pil_image(data[user_id][-1])
        style = take_pil_image(file_id)

        img = inference(content, style)
        if not os.path.exists('static'):
            os.mkdir('static')
        img.save(f'static/{user_id}.png', format='PNG')

        del data[user_id]
    else:
        data[user_id] = [file_id]


def inference(content: Image, style: Image) -> Image:
    imsize = 256 # if torch.cuda.is_available() else 128
    size_image = ts.calc_size(content, imsize=imsize)

    content_img = ts.image_loader(content,
                                  size_image=size_image)
    style_img = ts.image_loader(style,
                                size_image=size_image)

    assert style_img.size() == content_img.size(), \
    "we need to import style and content images of the same size"

    cnn_normalization_mean = torch.tensor([0.485, 0.456, 0.406]).to(ts.device)
    cnn_normalization_std = torch.tensor([0.229, 0.224, 0.225]).to(ts.device)

    # if not os.path.exists("model.pth"):
    #     cnn = models.vgg19(pretrained=True).features.to(ts.device).eval()
    #     torch.save(cnn, 'model.pth')
    # else:
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


def take_pil_image(file_id):
    uri = URI_INFO + file_id
    resp = requests.get(uri)
    img_path = resp.json()['result']['file_path']
    img = requests.get(URI + img_path)
    img = Image.open(io.BytesIO(img.content))
    return img


