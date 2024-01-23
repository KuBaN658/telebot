FROM python:3.10.13

WORKDIR /python

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install torch==2.1.2 torchvision==0.16.2

COPY . /python

CMD [ "python", "app.py" ]