# Step 1 - Build Front End Application
FROM node:16 AS build

# Copy the entire project - Webpack puts compiled assets into the Django folder
WORKDIR /app
COPY . .

RUN cd frontend && npm install --quiet --production
ENV ENV=prod
ENV STATIC_ASSET_CDN_URL=/static/
RUN cd frontend && npm run bundledjango


# Step 2 - Build Django Application
FROM python:3.10-slim as application

WORKDIR /app
COPY api /app/

# arm architecture platform builds need postgres drivers installing via apt
ARG TARGETARCH
RUN if [ "${TARGETARCH}" != "amd64" ]; then apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*; fi;

# Install re2
ARG GOOGLE_RE2_VERSION="0.2.20220401"
ARG TARGETPLATFORM
# re2 is broken on arm/v7 platform, so dont try to install it; fall back to standard re
RUN if [ "${TARGETPLATFORM}" != "linux/arm/v7" ]; then pip install google-re2==${GOOGLE_RE2_VERSION}; fi;

# Install python dependencies
RUN pip install -r requirements.txt --no-cache-dir --compile

# Compile static Django assets
RUN python /app/manage.py collectstatic --no-input

# Copy the compiled front end assets from the previous build step
COPY --from=build /app/api/static /app/static/
COPY --from=build /app/api/app/templates/webpack /app/app/templates/webpack

ARG ACCESS_LOG_LOCATION="/dev/null"
ENV ACCESS_LOG_LOCATION=${ACCESS_LOG_LOCATION}
ENV DJANGO_SETTINGS_MODULE=app.settings.production

EXPOSE 8000

USER nobody

ENTRYPOINT ["./scripts/run-docker.sh"]

# other options below are `migrate` or `serve`
CMD ["migrate-and-serve"]
