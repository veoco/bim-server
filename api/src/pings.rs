use std::sync::Arc;

use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
};
use axum_valid::Valid;
use serde_json::{json, Value};

use crate::extractors::ApiClient;
use crate::AppState;
use server_service::{Mutation as MutationCore, PingCreate, PingFilter, Query as QueryCore};

pub async fn create_ping_client(
    State(state): State<Arc<AppState>>,
    _: ApiClient,
    Path((mid, tid)): Path<(i32, i32)>,
    Valid(Json(ping_create)): Valid<Json<PingCreate>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        if let Ok(Some(target)) = QueryCore::find_target_by_id(&state.conn, tid).await {
            if let Ok(_) =
                MutationCore::create_ping(&state.conn, ping_create, machine.id, target.id).await
            {
                let _ = MutationCore::update_machine(&state.conn, machine.id).await;
                let _ = MutationCore::update_target(&state.conn, target.id).await;
                res = json!({"msg": "success"});
                status = StatusCode::OK;
            }
        }
    }
    (status, Json(res))
}

pub async fn list_pings(
    State(state): State<Arc<AppState>>,
    Path((mid, tid, delta)): Path<(i32, i32, String)>,
    Query(form): Query<PingFilter>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    let ipv6 = form.ipv6.unwrap_or(false);

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        if let Ok(Some(target)) = QueryCore::find_target_by_id(&state.conn, tid).await {
            if let Ok(pings) = QueryCore::find_pings_by_machine_id_and_target_id(
                &state.conn,
                machine.id,
                target.id,
                &delta,
                ipv6,
            )
            .await
            {
                let mut outputs = vec![];
                for p in pings {
                    outputs.push((p.created.and_utc().timestamp(), p.min, p.avg, p.fail));
                }
                res = json!({
                    "results": outputs,
                });
                status = StatusCode::OK;
            }
        }
    }
    (status, Json(res))
}
