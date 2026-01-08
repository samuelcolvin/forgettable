use std::net::SocketAddr;

use sqlx::{
    ConnectOptions,
    postgres::{PgConnectOptions, PgPoolOptions},
};
use tracing::log::LevelFilter;

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

    // Create database pool with query logging
    let connect_options: PgConnectOptions = config.database_url.parse()?;
    let connect_options = connect_options.log_statements(LevelFilter::Info);
    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect_with(connect_options)
        .await?;

    // Build router
    let app = routes::create_router(pool);

    // Start server
    let addr = SocketAddr::from(([0, 0, 0, 0], config.port));
    tracing::info!("Listening on {}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await?;
    axum::serve(listener, app).await?;

    Ok(())
}
