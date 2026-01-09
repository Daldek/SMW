FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY domain/ domain/
COPY providers/ providers/
COPY visualization/ visualization/
COPY gui/ gui/

EXPOSE 8501

CMD ["streamlit", "run", "gui/app.py", "--server.address=0.0.0.0"]
