FROM mcr.microsoft.com/playwright/python:v1.58.0-jammy

WORKDIR /workspace

COPY app/requirements.txt /workspace/requirements.txt

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /workspace/requirements.txt

EXPOSE 8888

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
