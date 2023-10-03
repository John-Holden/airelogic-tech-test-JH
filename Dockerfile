FROM python:bookworm

WORKDIR /usr/src/app
COPY backend.py .
COPY requirements.txt .
COPY QUESTION_CONF.toml /etc
RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x backend.py

# Placeholder to keep container running
CMD [ "sleep", "10h" ] 


