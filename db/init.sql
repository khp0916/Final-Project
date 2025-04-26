-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables
CREATE TABLE IF NOT EXISTS member (
    member_id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(6) NOT NULL,
    role VARCHAR(255),
    join_date TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS category (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(50) NOT NULL,
    category_icon VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS product (
    product_id SERIAL PRIMARY KEY,
    category_id INTEGER NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category(category_id)
);

CREATE TABLE IF NOT EXISTS favorite (
    favorite_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    member_id INTEGER NOT NULL,
    FOREIGN KEY (product_id) REFERENCES product(product_id),
    FOREIGN KEY (member_id) REFERENCES member(member_id)
);

CREATE TABLE IF NOT EXISTS query_history (
    query_id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    query_text VARCHAR(255) NOT NULL,
    response_text TEXT NOT NULL,
    query_time BIGINT NOT NULL,
    member_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS langchain_pg_collection (
    uuid UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cmetadata JSONB
);

CREATE TABLE IF NOT EXISTS langchain_pg_embedding (
    id SERIAL PRIMARY KEY,
    collection_id UUID NOT NULL,
    embedding vector NOT NULL,
    document TEXT NOT NULL,
    cmetadata JSONB,
    custom_id TEXT,
    FOREIGN KEY (collection_id) REFERENCES langchain_pg_collection(uuid)
); 