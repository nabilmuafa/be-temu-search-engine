FROM python:3.13

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && \
	apt-get install -y pkg-config cmake && \
	rm -rf /var/lib/apt/lists/* && \
	pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
