FROM python:3.7

RUN apt-get update \
    && apt-get install -y \
    lsb-release

RUN sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
RUN wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

RUN apt-get update \
    && apt-get install -y \
        nmap \
        vim \
        netcat \
        net-tools \
        iputils-ping \
        postgresql-client-10

COPY . /app
WORKDIR /app/chomsky

RUN pip install -r requirements.txt

# The EXPOSE command makes the port 80 accessible to the outside world (our flask service runs on port 80;
# we need this port inside the container to be accessible outside the container).
EXPOSE 8000

# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--access_log=/app/vinsight/accesslogfile.txt", "--root-path", "/api/v1"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--root-path", "/api/v1"]
