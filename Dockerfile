# Use an official Python runtime as a parent image
FROM python:3.12-slim as builder

# Set the working directory in the container
WORKDIR /usr/src/app

# Install any dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /venv \
    && /venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY  app.py app.py
COPY  static/ static/
COPY  templates templates

WORKDIR /usr/src/app/static
# Install nodejs and npm
RUN apt-get update && apt-get install -y nodejs npm
RUN npm install

RUN npx tailwindcss -i ./src/style.css -o css/main.css


# Use multi-stage builds to create a smaller final image
FROM python:3.12-slim
COPY --from=builder /venv /venv
WORKDIR /usr/src/app
COPY --from=builder /usr/src/app/ /usr/src/app/

# Ensure the script runs in a production environment
ENV FLASK_ENV=production

# Run the application with Gunicorn
CMD ["/venv/bin/gunicorn", "-b", "0.0.0.0:8080", "app:app"]
