FROM python:3-alpine

# Create app directory
WORKDIR /app

# Install app dependencies
COPY venv_requirements.txt ./

RUN pip install -r venv_requirements.txt

# Bundle app source
COPY . .

EXPOSE 5000
CMD [ "flask", "run","--host","0.0.0.0","--port","5000"]