use axum::{
    Router,
    routing::{delete, get, post},
};
use sqlx::PgPool;

use crate::handlers::entries;

pub fn create_router(pool: PgPool) -> Router {
    Router::new()
        // Entry operations - more specific routes first
        .route("/project/{project}/get/{*key}", get(entries::get_entry))
        .route("/project/{project}/list/", get(entries::list_entries_all))
        .route("/project/{project}/list/{*prefix}", get(entries::list_entries))
        // Catch-all routes for store and delete
        .route("/project/{project}/{*key}", post(entries::store_entry))
        .route("/project/{project}/{*key}", delete(entries::delete_entry))
        .with_state(pool)
}
