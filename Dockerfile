FROM ghcr.nju.edu.cn/xinnan-tech/xiaozhi-esp32-server:server_latest

WORKDIR /opt/xiaozhi-esp32-server

COPY server/main/xiaozhi-server/ /opt/xiaozhi-esp32-server/

RUN mkdir -p /opt/xiaozhi-esp32-server/data /opt/xiaozhi-esp32-server/tmp

