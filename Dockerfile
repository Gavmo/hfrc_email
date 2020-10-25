
FROM python:latest

ARG build_server=None
ARG build_port=None
ARG build_user=None
ARG build_secret=None


ENV IMAPSERVER=$build_server
ENV IMAPPORT=$build_port
ENV IMAPUSERNAME=$build_user
ENV IMAPSECRET=$build_secret

WORKDIR /usr/src/hfrc_email

COPY . .

RUN python scripts/check_email.py
