FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_PORT=8501

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod 755 /app/start.sh \
    && useradd --create-home --uid 10001 --shell /usr/sbin/nologin payguard \
    && chown -R payguard:payguard /app

USER payguard
EXPOSE 3000
CMD ["/app/start.sh"]
