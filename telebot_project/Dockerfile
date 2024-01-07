FROM python:3.10.13

WORKDIR /python

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /python

CMD [ "python", "app.py" ]