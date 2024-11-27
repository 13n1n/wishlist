FROM python:3.12


RUN apt update && apt install -y ffmpeg mediainfo && pip install poetry poetry-plugin-export


WORKDIR /app

ADD pyproject.toml poetry.lock ./
RUN bash -c 'pip install -r <(poetry export)'
ADD . ./

CMD ["python", "-m", "wishlist"]