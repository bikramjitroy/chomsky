FROM rasa/rasa-sdk:2.1.2

 # The Rasa SDK image runs as non-root user by default. Hence, you have to switch
 # back to the `root` user if you want to install additional dependencies
SHELL ["/bin/bash", "-c"]
USER root

RUN apt-get update -qq && \
  apt-get install -y --no-install-recommends \
  build-essential && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* 

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

# COPY . .
# RUN pip install -e . --no-cache-dir

VOLUME ["/app/actions"]

EXPOSE 5055


# USER root
# COPY . /action
# WORKDIR /action
# RUN pip3 install requirements.txt

# Switch back to a non-root user
USER 1001
CMD ["start", "--actions", "actions"]
