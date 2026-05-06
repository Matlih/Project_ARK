CREATE TABLE IF NOT EXISTS rejection_events (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(100),
    scene_id VARCHAR(200),
    gate_name VARCHAR(50),
    fail_reason VARCHAR(200),
    cloud_pct FLOAT,
    compute_saved_hrs FLOAT,
    compute_saved_usd FLOAT,
    analyst_hrs_saved FLOAT,
    peso_loss_prevented FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ard_certified (
    id SERIAL PRIMARY KEY,
    scene_id VARCHAR(200),
    event_id VARCHAR(100),
    certified_at TIMESTAMP DEFAULT NOW(),
    gate1_confidence FLOAT,
    gate2_cloud_pct FLOAT,
    gate3_ndvi_mean FLOAT
);