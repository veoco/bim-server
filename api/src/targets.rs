use std::sync::Arc;

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use axum_valid::Valid;
use serde_json::{json, Value};

use crate::extractors::{AdminUser, ApiClient};
use crate::AppState;
use server_service::{
    Mutation as MutationCore, Query as QueryCore, TargetCreateAdmin, TargetPublic,
};

pub async fn list_targets(State(state): State<Arc<AppState>>) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(targets) = QueryCore::find_targets(&state.conn).await {
        let mut outputs = vec![];
        for t in targets {
            outputs.push(TargetPublic {
                id: t.id,
                name: t.name,
                created: t.created,
                updated: t.updated,
            });
        }
        res = json!(outputs);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn list_targets_client(
    State(state): State<Arc<AppState>>,
    _: ApiClient,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(targets) = QueryCore::find_targets(&state.conn).await {
        res = json!(targets);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn create_target_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Valid(Json(target_create)): Valid<Json<TargetCreateAdmin>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(_)) = QueryCore::find_target_by_name(&state.conn, &target_create.name).await {
        status = StatusCode::CONFLICT;
        res = json!({"msg": "already exists"});
    } else {
        match MutationCore::create_target(&state.conn, &target_create).await {
            Ok(_) => {
                status = StatusCode::CREATED;
                res = json!({"msg": "success"});
            }
            Err(_) => {}
        }
    }

    (status, Json(res))
}

pub async fn edit_target_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(tid): Path<i32>,
    Valid(Json(target_create)): Valid<Json<TargetCreateAdmin>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(target)) = QueryCore::find_target_by_id(&state.conn, tid).await {
        let _ = MutationCore::edit_target(&state.conn, target.id, &target_create).await;
        res = json!({"msg": "success"});
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn list_targets_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(targets) = QueryCore::find_targets(&state.conn).await {
        res = json!(targets);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn get_target_by_tid_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(tid): Path<i32>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(target)) = QueryCore::find_target_by_id(&state.conn, tid).await {
        res = json!(target);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn delete_target_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(tid): Path<i32>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(_)) = QueryCore::find_target_by_id(&state.conn, tid).await {
        let _ = MutationCore::delete_target(&state.conn, tid).await;
        res = json!({"msg": "success"});
        status = StatusCode::OK;
    }

    (status, Json(res))
}
