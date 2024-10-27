FROM python:3.10-slim
LABEL authors="sukantaroy"

# Use the official Python image as a base

ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY Pipfile .
COPY Pipfile.lock .

# Install dependencies
RUN pip install pipenv
RUN pipenv requirements > requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 8000 for the FastAPI server
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
