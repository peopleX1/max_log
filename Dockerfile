###########
# BUILDER #
###########

# pull official base image
FROM ubuntu:22.04 as builder
# set work directory
WORKDIR /usr/src/cbr

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

# install psycopg2 dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        netcat \
        nano \
        unzip \
        zip \
        postgresql \
        libpq-dev \
        gcc \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-wheel \
        musl-dev \
        locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# copy project
RUN pip install --upgrade pip
RUN pip install wheel
COPY . .

# install dependencies
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/cbr/wheels -r requirements.txt


#########
# FINAL #
#########

# pull official base image
FROM ubuntu:22.04

# create directory for the app user
RUN mkdir -p /home/cbr

# set default timezone
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        netcat \
        nano \
        unzip \
        zip \
        postgresql \
        libpq-dev \
        gcc \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-wheel \
        musl-dev \
        locales && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# генерация и установка локалей
RUN locale-gen en_US.UTF-8 ru_RU.UTF-8 && update-locale

# Create a user group
#RUN addgroup cbr-group

# Create a user
#RUN useradd -ms /bin/bash  cbr-user

# Chown all the files to the app user.
#RUN chown -R cbr-user:cbr-group /usr/src/

# create the appropriate directories
ENV HOME=/home/cbr
ENV APP_HOME=/home/cbr/web
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV PYTHONIOENCODING=utf-8
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update && apt-get install libpq-dev
COPY --from=builder /usr/src/cbr/wheels /wheels
COPY --from=builder /usr/src/cbr/requirements.txt .

RUN pip install --upgrade pip
RUN pip install wheel
RUN pip install --no-cache /wheels/*

# copy entrypoint.prod.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g'  $APP_HOME/entrypoint.sh
RUN chmod +x  $APP_HOME/entrypoint.sh

# copy project
COPY . $APP_HOME

# chown all the files to the app user
#RUN chown -R cbr-user:cbr-group $APP_HOME

# change to the app user
#USER cbr-user

# run entrypoint.prod.sh
ENTRYPOINT [ "sh", "entrypoint.sh" ]
