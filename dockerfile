FROM python:3.9-slim
COPY . /srv/multilingual-txt-sim
WORKDIR /srv/multilingual-txt-sim

RUN mkdir /.cache && \
    chmod a+rwx -R /.cache

RUN mkdir /cache && \
    chmod a+rwx -R /cache

RUN mkdir /cache/hf && \
    chmod a+rwx -R /cache/hf

ENV TRANSFORMERS_CACHE=/cache/hf \
    HUGGINGFACE_HUB_CACHE=${TRANSFORMERS_CACHE} \
    HF_HOME=${TRANSFORMERS_CACHE} \
    SENTENCE_TRANSFORMERS_HOME=${TRANSFORMERS_CACHE} 


RUN apt-get clean \
    && apt-get -y update

RUN apt-get -y install nginx \
    && apt-get -y install python3-dev \
    && apt-get -y install build-essential

RUN pip install -r requirements.txt --src /usr/local/src

COPY nginx.conf /etc/nginx
RUN chmod +x ./start.sh
CMD ["./start.sh"]
