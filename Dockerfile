FROM python:3.9-slim-bullseye

RUN apt update && apt install -y gcc git

RUN pip install --no-cache-dir cython
RUN pip install --no-cache-dir cryptofeed
RUN pip install --no-cache-dir redis
RUN pip install --no-cache-dir pymongo[srv]
RUN pip install --no-cache-dir motor
RUN pip install --no-cache-dir asyncpg

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY crypto_load_test.py /crypto_load_test.py

ENTRYPOINT ["python"]
CMD ["/crypto_load_test.py"]
