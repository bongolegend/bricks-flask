FROM amancevice/pandas:0.24.2-slim
# RUN adduser -D bricks

# necessary to install C libs like numpy
# RUN apk add libc-dev
# RUN apk add build-essential

# copy project files to a non-system root
WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN python -m venv venv

RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

COPY . .
# allow the boot.sh to be executable
RUN chmod +x boot.sh

# expose a port that matches your flask port
EXPOSE 8000

CMD ["./boot.sh"]

# TODO create a new user to run this