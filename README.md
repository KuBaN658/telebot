# Tелеграм бот magic photo

## Описание проекта
**Это бот который может переносить стиль с одной фотографии на другую.**
![Пример работы.](https://github.com/KuBaN658/telebot/blob/main/image_readme_tgbot.PNG)


## Запуск проекта
1. Скачать проект 
`git clone https://github.com/KuBaN658/telebot.git`
2. Перейти в директорию /telebot_project
3. Создаем docker-образ
   `docker build -t <название образа> .`
4. Создаем docker-контейнер и запускаем его
  `docker run --gpus all -e TG_BOT_TOKEN=<токен твоего бота> -e ADMIN_IDS=<твой telegram id> <название образа>`

  `--gpus all` - добавляем если хотим использовать видеокарту.
