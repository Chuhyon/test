CREATE TABLE IF NOT EXISTS stores (
    store_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id UUID NOT NULL,
    store_name VARCHAR(100) NOT NULL,
    business_type VARCHAR(50) NOT NULL,
    region VARCHAR(100),
    business_registration_no VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS platform_accounts (
    platform_account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    account_ref VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    connected_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS consents (
    consent_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    owner_id UUID NOT NULL,
    consent_type VARCHAR(30) NOT NULL,
    allowed_scopes TEXT NOT NULL,
    purpose VARCHAR(200) NOT NULL,
    retention_period VARCHAR(50) NOT NULL,
    consented_at TIMESTAMP NOT NULL DEFAULT now(),
    revoked_at TIMESTAMP,
    revoke_reason VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS data_import_jobs (
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    import_method VARCHAR(20) NOT NULL,
    file_type VARCHAR(20),
    data_category VARCHAR(30) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    records_count INTEGER,
    error_message TEXT,
    consent_id UUID REFERENCES consents(consent_id),
    uploaded_at TIMESTAMP NOT NULL DEFAULT now(),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS raw_data (
    raw_data_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES data_import_jobs(job_id),
    file_hash VARCHAR(64) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    storage_path VARCHAR(500) NOT NULL,
    uploaded_at TIMESTAMP NOT NULL DEFAULT now(),
    retention_until TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS settlements (
    settlement_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    job_id UUID REFERENCES data_import_jobs(job_id),
    settlement_date DATE NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    gross_sales DECIMAL(15,2) NOT NULL,
    total_deductions DECIMAL(15,2) NOT NULL,
    net_deposit DECIMAL(15,2) NOT NULL,
    effective_fee_rate DECIMAL(5,4),
    currency VARCHAR(3) NOT NULL DEFAULT 'KRW',
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS settlement_fee_items (
    fee_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    settlement_id UUID NOT NULL REFERENCES settlements(settlement_id),
    fee_type VARCHAR(50) NOT NULL,
    fee_label VARCHAR(100),
    amount DECIMAL(15,2) NOT NULL,
    rate DECIMAL(5,4),
    base_amount DECIMAL(15,2),
    source_row_id VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    job_id UUID REFERENCES data_import_jobs(job_id),
    order_date DATE NOT NULL,
    order_time TIME,
    order_amount DECIMAL(15,2) NOT NULL,
    delivery_fee DECIMAL(15,2),
    discount_amount DECIMAL(15,2),
    order_status VARCHAR(20) NOT NULL,
    order_type VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID NOT NULL REFERENCES orders(order_id),
    menu_name VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(15,2) NOT NULL,
    total_price DECIMAL(15,2) NOT NULL
);

CREATE TABLE IF NOT EXISTS ads (
    ad_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    job_id UUID REFERENCES data_import_jobs(job_id),
    ad_type VARCHAR(50) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    spend DECIMAL(15,2) NOT NULL,
    impressions INTEGER,
    clicks INTEGER,
    attributed_orders INTEGER,
    attributed_sales DECIMAL(15,2),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS menus (
    menu_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    menu_name VARCHAR(200) NOT NULL,
    price DECIMAL(15,2) NOT NULL,
    category VARCHAR(50),
    cost DECIMAL(15,2),
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    store_id UUID NOT NULL REFERENCES stores(store_id),
    platform VARCHAR(20) NOT NULL,
    metric_date DATE NOT NULL,
    total_orders INTEGER NOT NULL,
    completed_orders INTEGER NOT NULL,
    cancelled_orders INTEGER,
    gross_sales DECIMAL(15,2) NOT NULL,
    net_sales DECIMAL(15,2),
    ad_spend DECIMAL(15,2),
    delivery_fee_income DECIMAL(15,2),
    delivery_fee_expense DECIMAL(15,2),
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE(store_id, platform, metric_date)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id UUID NOT NULL,
    actor_type VARCHAR(20) NOT NULL,
    store_id UUID,
    action VARCHAR(50) NOT NULL,
    data_scope VARCHAR(50),
    detail TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

CREATE INDEX idx_settlements_store_date ON settlements(store_id, settlement_date);
CREATE INDEX idx_fee_items_settlement ON settlement_fee_items(settlement_id);
CREATE INDEX idx_orders_store_date ON orders(store_id, order_date);
CREATE INDEX idx_daily_metrics_store_date ON daily_metrics(store_id, metric_date);
CREATE INDEX idx_ads_store_period ON ads(store_id, period_start);
CREATE INDEX idx_audit_logs_store_date ON audit_logs(store_id, created_at);
CREATE INDEX idx_consents_store_type ON consents(store_id, consent_type);
CREATE INDEX idx_raw_data_retention ON raw_data(retention_until);
