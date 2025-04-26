FROM postgres:latest

# Install pgvector extension
RUN apt-get update && \
    apt-get install -y git postgresql-server-dev-all gcc make && \
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    make && \
    make install && \
    cd .. && \
    rm -rf pgvector && \
    apt-get remove -y git postgresql-server-dev-all gcc make && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Create extension on database initialization
COPY init.sql /docker-entrypoint-initdb.d/ 