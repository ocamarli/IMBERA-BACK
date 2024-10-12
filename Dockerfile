FROM python:3.10
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
RUN . "${VIRTUAL_ENV}/bin/activate"
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5000
COPY ./rutas ./rutas
COPY ./data ./data
COPY ./app.py ./
COPY ./.env ./
COPY ./config.py ./
COPY ./User.py ./
COPY ./requirements.txt ./

RUN pip install -r ./requirements.txt
CMD ["python", "app.py"]
