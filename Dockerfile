FROM alpine:latest as base

FROM base as builder

RUN mkdir -p /install /app /app/downloads
WORKDIR /app

COPY requirements.txt requirements.txt

RUN apk add --no-cache --virtual .build-deps alpine-sdk gcc g++ make linux-headers python3-dev python3 py3-pip
RUN pip3 install --target=/install -U -r requirements.txt

WORKDIR /app

FROM base

RUN apk add --no-cache python3 py3-pip

COPY --from=builder /install /install


COPY --from=docker.io/mwader/static-ffmpeg:5.0 /ffmpeg /usr/local/bin/
COPY --from=docker.io/mwader/static-ffmpeg:5.0 /ffprobe /usr/local/bin/
COPY ../ /app

ENV PATH="/usr/local/bin:$PATH"
ENV LD_LIBRARY_PATH=/usr/local/lib:/usr/local/lib64
ENV PYTHONPATH=/install
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ENTRYPOINT ["/usr/bin/python3", "-u"]
