FROM python:3.9.1-slim-buster

LABEL org.opencontainers.image.authors="FNNDSC <dev@babyMRI.org>" \
      org.opencontainers.image.title="ChRIS Age Calculation" \
      org.opencontainers.image.description="A ChRIS ds plugin for calculating the age between two CSV columns containing dates and outputs result to another column as days or months"

WORKDIR /usr/local/src

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
RUN pip3 install .

CMD ["ageatscan", "--help"]
