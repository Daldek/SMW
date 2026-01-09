FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY requirements.txt .
COPY domain/ domain/
COPY providers/ providers/
COPY visualization/ visualization/
COPY gui/ gui/

RUN pip install --no-cache-dir -e .

EXPOSE 8501

CMD ["streamlit", "run", "gui/app.py", "--server.address=0.0.0.0", "--server.headless=true"]
