use std::env;

use thiserror::Error;

#[derive(Error, Debug)]
pub enum ConfigError {
    #[error("DATABASE_URL environment variable is not set")]
    MissingDatabaseUrl,
    #[error("PORT environment variable is not a valid number")]
    InvalidPort,
}

pub struct Config {
    pub database_url: String,
    pub port: u16,
}

impl Config {
    pub fn from_env() -> Result<Self, ConfigError> {
        let database_url = env::var("DATABASE_URL").map_err(|_| ConfigError::MissingDatabaseUrl)?;

        let port = env::var("PORT")
            .unwrap_or_else(|_| "3003".to_string())
            .parse()
            .map_err(|_| ConfigError::InvalidPort)?;

        Ok(Self { database_url, port })
    }
}
