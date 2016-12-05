FROM python:3.5

# Set timezone
RUN ln -fs /usr/share/zoneinfo/Europe/Stockholm /etc/localtime && dpkg-reconfigure -f noninteractive tzdata

# Copy application
COPY . /fikabot
WORKDIR /fikabot

# Install application
RUN pip3 install --requirement requirements.txt

# Export tokens
# ENV SLACK_BOT_TOKEN=<slack_bot_token>
# ENV BOT_ID=<bot id>

# Start bot
ENTRYPOINT ["fikabot/run_fikabot.py"]
