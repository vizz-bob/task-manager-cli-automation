# ============================================================
# Dockerfile — Personal Task Manager CLI + Web Automation
# Base: Python 3.11 slim (lightweight Linux)
# ============================================================

FROM python:3.11-slim

# ── System dependencies for Playwright + curl + jq ──────────
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    bash \
    cron \
    # Playwright / Chromium system deps
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# ── Set working directory ────────────────────────────────────
WORKDIR /app

# ── Install Python dependencies ──────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Install Playwright Chromium browser ──────────────────────
RUN python3 -m playwright install chromium

# ── Copy all project scripts ─────────────────────────────────
COPY step1_fetch.sh .
COPY step2_filter.py .
COPY step3_validate.py .
COPY step4_cron_setup.sh .
COPY step5_playwright.py .
COPY step6_cua_trajectories.md .
COPY SETUP_GUIDE.md .

# ── Make bash scripts executable ─────────────────────────────
RUN chmod +x step1_fetch.sh step4_cron_setup.sh

# ── Create output directories ─────────────────────────────────
RUN mkdir -p /app/output /tmp

# ── Default command: show available steps ────────────────────
CMD ["/bin/bash", "-c", "echo '' && echo '=====================================' && echo '  Task Manager — Ready' && echo '=====================================' && echo '  Run a step:' && echo '    docker exec -it taskmanager bash' && echo '  Then inside container:' && echo '    ./step1_fetch.sh' && echo '    python3 step2_filter.py --status pending' && echo '    python3 step3_validate.py' && echo '    ./step4_cron_setup.sh' && echo '    python3 step5_playwright.py' && echo '=====================================' && tail -f /dev/null"]
