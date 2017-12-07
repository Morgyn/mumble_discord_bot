FROM python:3.6.3-alpine3.6

RUN set -ex \
  && apk add --no-cache --virtual .build-deps \
    g++ \
    bzip2-dev \
    openssl-dev \
  && pip install --global-option=build_ext --global-option="-D__USE_UNIX98" zeroc-ice \
  && pip install requests pytz \
  && apk del .build-deps \
  && find /usr/local -depth \
       \( \
         \( -type d -a \( -name test -o -name tests \) \) \
         -o \
         \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
       \) -exec rm -rf '{}' +;

WORKDIR /app
COPY Murmur.ice discord_bot.py ./

CMD ["python", "discord_bot.py"]
