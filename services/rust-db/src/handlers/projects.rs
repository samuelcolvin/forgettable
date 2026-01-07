use axum::{extract::State, Json};
use sqlx::PgPool;
use uuid::Uuid;

use crate::error::Result;
use crate::models::Project;

pub async fn create_project(State(pool): State<PgPool>) -> Result<Json<Project>> {
    let id: Uuid = sqlx::query_scalar("INSERT INTO projects DEFAULT VALUES RETURNING id")
        .fetch_one(&pool)
        .await?;

    Ok(Json(Project { id }))
}
