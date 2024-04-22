FROM mambaorg/micromamba:1.5.8

# renaming the environment to base
# see https://micromamba-docker.readthedocs.io/en/latest/quick_start.html
COPY --chown=$MAMBA_USER:$MAMBA_USER environment.yml /tmp/env.yaml
RUN   sed -i "s|yourapp-backend|base |g" /tmp/env.yaml

WORKDIR /app
COPY . .

RUN micromamba install --yes --file /tmp/env.yaml && \
    micromamba clean --all --yes

# (otherwise python will not be found)
ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -m pip install --no-cache-dir -e .

EXPOSE 5000

CMD python yourapp/scripts/server.py --host "0.0.0.0" --port 5000