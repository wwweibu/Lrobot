FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# 拷贝主控文件
COPY command.py .

# 拷贝密钥权限配置文件
COPY key.sh /app/key.sh
RUN chmod +x /app/key.sh

# 默认执行
ENTRYPOINT ["/app/key.sh"]

CMD ["python", "command.py"]