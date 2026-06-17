
FROM python:3.11-slim

WORKDIR /app

# System deps for paho-mqtt / dotenv (minimal, slim image)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# No EXPOSE needed -- this is a worker, not a web service.
# It only makes outbound HTTP/MQTT calls to BACKEND_URL.
CMD ["python", "mqtt_simulator.py"]
