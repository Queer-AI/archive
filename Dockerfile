FROM ubuntu:16.04

# Pick up some TF dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        libfreetype6-dev \
        libpng12-dev \
        libzmq3-dev \
        pkg-config \
        python \
        python-dev \
        python-setuptools \
        rsync \
        software-properties-common \
        unzip \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN easy_install pip

RUN pip --no-cache-dir install \
        autobahn \
        numpy \
        six \
        twisted

# Install TensorFlow CPU version from central repo
RUN pip --no-cache-dir install \
    http://storage.googleapis.com/tensorflow/linux/cpu/tensorflow-1.0.1-cp27-none-linux_x86_64.whl

WORKDIR /var/www

ENV MODEL_ID 170600

RUN set -e;\
  curl -sLo data/translate.ckpt-${MODEL_ID}.data-00000-of-00001 https://s3-us-west-1.amazonaws.com/queer-ai/model_data/translate.ckpt-${MODEL_ID}.data-00000-of-00001;\
 curl -sLo data/translate.ckpt-${MODEL_ID}.index https://s3-us-west-1.amazonaws.com/queer-ai/model_data/translate.ckpt-${MODEL_ID}.index;\
curl -sLo data/translate.ckpt-${MODEL_ID}.meta https://s3-us-west-1.amazonaws.com/queer-ai/model_data/translate.ckpt-${MODEL_ID}.meta;

# Copy sample .
COPY api api
COPY seq2seq seq2seq
COPY util util
COPY train train
COPY config.json config.json
COPY serve.py serve.py


EXPOSE 8000

CMD ["python", "serve.py"]
