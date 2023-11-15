FROM python:3.10-alpine
 
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
 
COPY app.py app.py

ENV PYTHONUNBUFFERED=1

EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]
