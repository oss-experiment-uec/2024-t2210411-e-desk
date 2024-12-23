FROM python:3.9.10-bullseye

# Set Timezone (maybe unnecessary)
# ENV TZ=Asia/Tokyo
# RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
#     echo $TZ > /etc/timezone

RUN apt update && apt upgrade -y

COPY . /e-desk
WORKDIR /e-desk

RUN pip3 install --no-cache-dir -r requirements.txt

# setting locale may be unnecessary #
# in my environment, the bash prompt is broken in the docker container # 
RUN apt-get install -y locales
RUN echo "ja_JP UTF-8" > /etc/locale.gen
RUN locale-gen

#CMD [ "./Start.py" ]
