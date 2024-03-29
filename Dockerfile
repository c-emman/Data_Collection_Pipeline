FROM python:3.8-slim-bullseye as base

FROM base as builder

RUN mkdir /install
WORKDIR /install

RUN pip install --upgrade pip

FROM base

COPY requirements.txt /requirements.txt

RUN pip install -r /requirements.txt

COPY --from=builder  /install  /usr/local/

RUN apt-get update && apt-get install -y gnupg

RUN  apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/listssudo/*

RUN apt-get update && apt-get install -y curl

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -

RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'

RUN apt-get update && apt-get install -y google-chrome-beta

RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/104.0.5112.29/chromedriver_linux64.zip

RUN apt-get install -yqq unzip 

RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

COPY . /web_scraper_project
WORKDIR /web_scraper_project

ENTRYPOINT [ "python3", "-m", "web_scraper" ]