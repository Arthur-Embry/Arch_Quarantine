# add python env
FROM python:3.10
    
# make a directory for the app code
WORKDIR /code

# mount the re requirements on code file
COPY ./requirements.txt /code/requirements.txt

# install python dependencies and handle caching
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# mount the app on code file
COPY ./app /code/app

# run the app (uvicorn)
CMD ["uvicorn", "app.api.server:app","--reload", "--host", "0.0.0.0", "--port", "8080"]