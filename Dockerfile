FROM python:3

WORKDIR "/app/qrcodeocr"


# Install dependencies using godep first

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Copy the local package files to the container's workspace.
# ADD . /go/src/gitlab.com/Howfintech/hopp-worker-service

COPY . .

# COPY ./qrcodeocr/ini/config.prod.ini ./qrcodeocr/ini/config.ini

# COPY ./qrcodeocr/ini/logging.prod.ini ./qrcodeocr/ini/logging.ini

ENV PYTHONPATH "${PYTHONPATH}:/app/qrcodeocr"

CMD [ "python", "/app/qrcodeocr/api.py", "-s data-api -e local" ]
# CMD ["gunicorn", "qrcodeocr.app.api:app","-b", "0.0.0.0:5000", "-w", "3"]

# Document that the service listens on port 8080.
EXPOSE 5000
