FROM postgres:latest

# Install pgvector extension
RUN apt-get update && \
    apt-get install -y git postgresql-server-dev-16 gcc make && \
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && \
    cd pgvector && \
    PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config make && \
    PG_CONFIG=/usr/lib/postgresql/16/bin/pg_config make install && \
    cd .. && \
    rm -rf pgvector && \
    apt-get remove -y git postgresql-server-dev-16 gcc make && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy initialization scripts
COPY init.sql /docker-entrypoint-initdb.d/ 
