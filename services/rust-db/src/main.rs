use std::{net::SocketAddr, sync::Arc};

use sqlx::postgres::PgPoolOptions;

mod config;
mod error;
mod handlers;
mod models;
mod routes;

use config::Config;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize logfire (sets up tracing subscriber automatically)
    let logfire = logfire::configure()
        .with_service_name("rust-db")
        .finish()?;
    let _shutdown_guard = logfire.shutdown_guard();

    // Load configuration
    let config = Config::from_env()?;

    // Create database pool wrapped with sqlx-tracing for OTEL spans
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&config.database_url)
        .await?;
    let pool = Arc::new(sqlx_tracing::Pool::from(pool));

    // Build router
    let app = routes::create_router(pool);

    // Start server
    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    tracing::info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
