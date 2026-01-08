use axum::{
    Json,
    body::Bytes,
    extract::{Path, State},
    http::{HeaderMap, StatusCode, header},
    response::{IntoResponse, Response},
};
use uuid::Uuid;

use crate::{
    error::{AppError, Result},
    models::{Entry, KeyInfo},
};

type Pool = std::sync::Arc<sqlx_tracing::Pool<sqlx::Postgres>>;

pub async fn get_entry(State(pool): State<Pool>, Path((project, key)): Path<(Uuid, String)>) -> Result<Response> {
    let opt_entry: Option<Entry> = sqlx::query_as!(
        Entry,
        r#"
        SELECT mime_type, content
        FROM entries
        WHERE project_id = $1 AND key = $2
        "#,
        project,
        key
    )
    .fetch_optional(&*pool)
    .await?;

    if let Some(entry) = opt_entry {
        logfire::info!(
            "retrieved value project={project} key={key} mime_type={mime_type} size={size}",
            project = project.to_string(),
            key = key,
            mime_type = &entry.mime_type,
            size = entry.content.len()
        );

        Ok((StatusCode::OK, [(header::CONTENT_TYPE, entry.mime_type)], entry.content).into_response())
    } else {
        logfire::info!(
            "key not found project={project} key={key}",
            project = project.to_string(),
            key = &key,
        );
        Err(AppError::KeyNotFound(key))
    }
}

pub async fn list_entries_all(State(pool): State<Pool>, Path(project): Path<Uuid>) -> Result<Json<Vec<KeyInfo>>> {
    let entries: Vec<KeyInfo> = sqlx::query_as!(
        KeyInfo,
        r#"
        SELECT key, mime_type
        FROM entries
        WHERE project_id = $1
        ORDER BY key
        "#,
        project
    )
    .fetch_all(&*pool)
    .await?;

    Ok(Json(entries))
}

pub async fn list_entries(
    State(pool): State<Pool>,
    Path((project, prefix)): Path<(Uuid, String)>,
) -> Result<Json<Vec<KeyInfo>>> {
    // Escape SQL LIKE wildcards
    let pattern = format!(
        "{}%",
        prefix.replace('\\', "\\\\").replace('%', "\\%").replace('_', "\\_")
    );

    let entries: Vec<KeyInfo> = sqlx::query_as!(
        KeyInfo,
        r#"
        SELECT key, mime_type
        FROM entries
        WHERE project_id = $1 AND key LIKE $2
        ORDER BY key
        "#,
        project,
        pattern
    )
    .fetch_all(&*pool)
    .await?;

    Ok(Json(entries))
}

pub async fn store_entry(
    State(pool): State<Pool>,
    Path((project, key)): Path<(Uuid, String)>,
    headers: HeaderMap,
    body: Bytes,
) -> Result<StatusCode> {
    // Extract Content-Type, default to application/octet-stream
    let mime_type = headers
        .get(header::CONTENT_TYPE)
        .and_then(|v| v.to_str().ok())
        .unwrap_or("application/octet-stream")
        .to_string();

    // Create project if it doesn't exist
    sqlx::query("INSERT INTO projects (id) VALUES ($1) ON CONFLICT (id) DO NOTHING")
        .bind(project)
        .execute(&*pool)
        .await?;

    // Upsert entry
    sqlx::query(
        r#"
        INSERT INTO entries (project_id, key, mime_type, content, updated_at)
        VALUES ($1, $2, $3, $4, NOW())
        ON CONFLICT (project_id, key)
        DO UPDATE SET
            mime_type = EXCLUDED.mime_type,
            content = EXCLUDED.content,
            updated_at = NOW()
        "#,
    )
    .bind(project)
    .bind(&key)
    .bind(&mime_type)
    .bind(body.as_ref())
    .execute(&*pool)
    .await?;

    Ok(StatusCode::CREATED)
}

pub async fn delete_entry(State(pool): State<Pool>, Path((project, key)): Path<(Uuid, String)>) -> Result<StatusCode> {
    let result = sqlx::query("DELETE FROM entries WHERE project_id = $1 AND key = $2")
        .bind(project)
        .bind(&key)
        .execute(&*pool)
        .await?;

    if result.rows_affected() == 0 {
        return Err(AppError::KeyNotFound(key));
    }

    Ok(StatusCode::NO_CONTENT)
}
