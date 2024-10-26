# Используем Python 3.11
FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта
COPY . /app

# Устанавливаем зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Устанавливаем и настраиваем SSH-сервер (если нужен SSH-доступ)
RUN apt-get update && apt-get install -y openssh-server
RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config
RUN echo 'root:rootpassword' | chpasswd

# Открываем порты для SSH и Django-сервера
EXPOSE 22 8000

# Запускаем SSH и Django-сервер
CMD service ssh start && python /app/store/manage.py runserver 0.0.0.0:8000