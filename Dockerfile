FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

COPY app/ /app/app/
COPY doc/ /app/doc/
COPY README.md /app/README.md

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
