import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from PIL import Image
import torchvision.transforms as transforms
import torch.optim as optim
import copy
import warnings

warnings.filterwarnings('ignore')


class ContentLoss(nn.Module):

    def __init__(self, target: torch.tensor):
        super(ContentLoss, self).__init__()
        self.target = target.detach()

    def forward(self, input:torch.tensor) -> torch.tensor:
        self.loss = F.mse_loss(input, self.target)
        return input


class StyleLoss(nn.Module):

    def __init__(self, target_feature: torch.tensor):
        super(StyleLoss, self).__init__()
        self.target = self.gram_matrix(target_feature).detach()

    def forward(self, input: torch.tensor) -> torch.tensor:
        G = self.gram_matrix(input)
        self.loss = F.mse_loss(G, self.target)
        return input

    @staticmethod
    def gram_matrix(input: torch.tensor) -> torch.tensor:
        a, b, c, d = input.size()
        features = input.view(a * b, c * d)
        G = torch.mm(features, features.t())
        return G.div(a * b * c * d)


class Normalization(nn.Module):
    def __init__(self, mean, std):
        super(Normalization, self).__init__()
        # .view the mean and std to make them [C x 1 x 1] so that they can
        # directly work with image Tensor of shape [B x C x H x W].
        # B is batch size. C is number of channels. H is height and W is width.
        self.mean = torch.tensor(mean).view(-1, 1, 1).clone().detach()
        self.std = torch.tensor(std).view(-1, 1, 1).clone().detach()

    def forward(self, img: torch.tensor) -> torch.tensor:
        # normalize img
        return (img - self.mean) / self.std


def calc_size(image_content: Image, imsize: int=512) -> tuple[int, int]:
    if image_content.width > image_content.height:
        return int(imsize / image_content.width * image_content.height), imsize
    return imsize, int(imsize / image_content.height * image_content.width)


def image_loader(image: Image, size_image: tuple[int, int]) -> torch.tensor:
    loader = transforms.Compose([
        transforms.Resize(size_image),
        transforms.ToTensor()])
    image = loader(image).unsqueeze(0)
    return image.to(device, torch.float)


def from_tensor_to_pil_image(tensor: torch.tensor) -> Image:
    unloader = transforms.ToPILImage()
    image = tensor.cpu().clone() 
    image = image.squeeze(0)  
    image = unloader(image)
    return image


def get_style_model_and_losses(cnn: torch.nn.modules.container.Sequential,
                                normalization_mean: torch.tensor, 
                                normalization_std: torch.tensor,
                               style_img: torch.tensor,
                               content_img: torch.tensor,
                               content_layers: str = ('conv_4'),
                               style_layers: tuple[str, str, str, str, str]=('conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5')):

    cnn = copy.deepcopy(cnn)

    normalization = Normalization(normalization_mean, normalization_std).to(device)

    content_losses = []
    style_losses = []

    model = nn.Sequential(normalization)

    i = 0
    for layer in cnn.children():
        if isinstance(layer, nn.Conv2d):
            i += 1
            name = 'conv_{}'.format(i)
        elif isinstance(layer, nn.ReLU):
            name = 'relu_{}'.format(i)
            layer = nn.ReLU(inplace=False)
        elif isinstance(layer, nn.MaxPool2d):
            name = 'pool_{}'.format(i)
        elif isinstance(layer, nn.BatchNorm2d):
            name = 'bn_{}'.format(i)
        else:
            raise RuntimeError('Unrecognized layer: {}'.format(layer.__class__.__name__))

        model.add_module(name, layer)

        if name in content_layers:
            target = model(content_img).detach()
            content_loss = ContentLoss(target)
            model.add_module("content_loss_{}".format(i), content_loss)
            content_losses.append(content_loss)

        if name in style_layers:
            target_feature = model(style_img).detach()
            style_loss = StyleLoss(target_feature)
            model.add_module("style_loss_{}".format(i), style_loss)
            style_losses.append(style_loss)

    for i in range(len(model) - 1, -1, -1):
        if isinstance(model[i], ContentLoss) or isinstance(model[i], StyleLoss):
            break

    model = model[:(i + 1)]

    return model, style_losses, content_losses


def get_input_optimizer(input_img: torch.tensor):
    optimizer = optim.LBFGS([input_img.requires_grad_()], lr=0.3)
    return optimizer


def run_style_transfer(cnn: torch.nn.modules.container.Sequential,
                       normalization_mean: torch.tensor,
                       normalization_std: torch.tensor,
                       content_img: torch.tensor, 
                       style_img: torch.tensor,
                       input_img: torch.tensor, 
                       num_steps: int=300,
                       style_weight: int=1000000,
                       content_weight: int=3):

    model, style_losses, content_losses = get_style_model_and_losses(cnn,
        normalization_mean, normalization_std, style_img, content_img)
    optimizer = get_input_optimizer(input_img)

    run = [0]
    while run[0] <= num_steps:

        def closure():
            input_img.data.clamp_(0, 1)

            optimizer.zero_grad()
            model(input_img)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.loss
            for cl in content_losses:
                content_score += cl.loss

            style_score *= style_weight
            content_score *= content_weight

            loss = style_score + content_score
            loss.backward()

            run[0] += 1

            return style_score + content_score

        optimizer.step(closure)

    input_img.data.clamp_(0, 1)

    return input_img

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


