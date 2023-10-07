# Используйте официальный образ Python
FROM python:3.11 AS build 


RUN mkdir app

WORKDIR /app

# Копирование исходного кода
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools whell && \
    pip install --user --no-cache-dir -r requirements.txt


RUN useradd -G users -U -m -s /bin/bash botenv && \
    chown botenv:botenv /app && \
    mkdir -p /home/botenv/.local/bin && \
    chown -R botenv:botenv /home/botenv && \
    cp -p -R /root/.cache/ /home/botenv/.cache/ && \
    chown -R botenv:botenv /home/botenv/.cache/

COPY . /app

FROM build AS base 
# Установка рабочего каталога

ENV PATH=/home/botenv/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH


ENTRYPOINT ["python", "botenv.py"]
