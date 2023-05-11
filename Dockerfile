FROM python:3.6

# 本地似乎需要echo -e来转义\n 线上不能有
RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo 'Asia/Shanghai' >/etc/timezone && \
    echo "deb http://mirrors.aliyun.com/debian bullseye main \n\
deb http://mirrors.aliyun.com/debian-security bullseye-security main \n\
deb http://mirrors.aliyun.com/debian bullseye-updates main \n\
" > /etc/apt/sources.list

# RUN apt-get update && apt-get install -y build-essential tcl && apt-get install -y redis-server

# workdir
WORKDIR /app

COPY . /app
RUN pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple && \
    chmod +x run.sh && chmod +x dev.sh && chmod +x prod.sh && chmod +x restart.sh && chmod +x gunicorn


#CMD ["scrapy","crawl","school_spider"]
#CMD ["python","app.py","runserver","-h","0.0.0.0", "-p", "8080"]
CMD ["/bin/sh","-c","./run.sh"]
