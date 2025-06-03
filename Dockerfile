FROM python:3.11-slim

# system dependencies
RUN apt-get update && apt-get install -y \
    wget curl unzip \
    firefox-esr \
    libgtk-3-0 libdbus-glib-1-2 libasound2 libx11-xcb1 libxt6 \
    && rm -rf /var/lib/apt/lists/*

# GeckoDriver (latest stable)
ENV GECKODRIVER_VERSION=0.34.0
RUN wget -O /tmp/geckodriver.tar.gz "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" \
    && tar -xzf /tmp/geckodriver.tar.gz -C /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && rm /tmp/geckodriver.tar.gz

WORKDIR /app

RUN echo -e '#!/bin/bash\nexec python main.py "$@"' > entrypoint.sh \
    && chmod +x entrypoint.sh

RUN useradd -ms /bin/bash scraper && \
    chown -R scraper:scraper /app

USER scraper

COPY --chown=scraper:scraper requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=scraper:scraper . .

VOLUME ["/app/exports", "/app/logs"]
ENTRYPOINT ["./entrypoint.sh"]
CMD ["--firefox", "--headless"]
