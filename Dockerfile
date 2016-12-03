FROM ubuntu:16.04

# Enable UTF-8 support
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install system packages
RUN apt update -q && \
    apt upgrade --yes && \
    apt install --yes python3-dev python3-pip

# Copy application
COPY . /fikabot
WORKDIR /fikabot

# Install application
RUN pip3 install --requirement requirements.txt

# Export tokens
# ENV SLACK_BOT_TOKEN=<your slack bot token>
# ENV BOT_ID=<your_bot_id>

# Start bot
ENTRYPOINT ["fikabot/run_fikabot.py"]
