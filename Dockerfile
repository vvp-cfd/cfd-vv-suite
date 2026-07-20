FROM python:3.11-slim

LABEL org.opencontainers.image.source="https://github.com/vvp-cfd/cfd-vv-suite"
LABEL org.opencontainers.image.description="CFD V&V Suite — CLI toolkit and test cases for verification and validation of CFD codes"
LABEL org.opencontainers.image.licenses="MIT"

COPY . /opt/cfdvv-suite
WORKDIR /opt/cfdvv-suite
RUN pip install --no-cache-dir -e tools/

ENTRYPOINT ["cfdvv"]
CMD ["--help"]
