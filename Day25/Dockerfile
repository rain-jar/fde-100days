#Build an image on top of an existing Python3.12 image ( aka current installed version of Python). 
#Slim means minimal version of that Python image.
FROM python:3.12-slim 

#Set /app as the working directory inside the image/container
WORKDIR /app

#Copy the requirements file into the /app directory
COPY requirements.txt .

#Install -into the image - all the dependencies listed in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#Copy the current directory on my machine to the current project directory (aka /app) of the image
COPY . .

#Execute these when a container starts from this image
#Essentially - Whena a container starts from this image - start FastAPI server on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]