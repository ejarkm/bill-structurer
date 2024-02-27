# Use an official Python runtime as a parent image
FROM python:3.10

# The environment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

# Setting PYTHONPATH so that the container knows where to look for modules
ENV PYTHONPATH /app:/app/src

RUN echo ${PYTHONPATH}
RUN echo ${INVOICE_API_KEY}

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . .

# Install any needed packages specified in Pipfile.lock
RUN pip install pipenv && pipenv install --system --deploy

# Run the command to start uWSGI
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]