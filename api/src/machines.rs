use std::sync::Arc;

use axum::{
    extract::{Path, State},
    http::StatusCode,
    Json,
};
use axum_client_ip::InsecureClientIp;
use axum_valid::Valid;
use serde_json::{json, Value};

use crate::extractors::{AdminUser, ApiClient};
use crate::AppState;
use server_service::{
    MachineCreate, MachineCreateAdmin, MachinePublic, MachineTargetsPublic,
    Mutation as MutationCore, Query as QueryCore, TargetPublic,
};

pub async fn create_machine_client(
    State(state): State<Arc<AppState>>,
    _: ApiClient,
    InsecureClientIp(ip): InsecureClientIp,
    Valid(Json(machine_create)): Valid<Json<MachineCreate>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    let ip = ip.to_string();

    if let Ok(Some(machine)) =
        QueryCore::find_machine_by_name(&state.conn, &machine_create.name).await
    {
        let form = MachineCreateAdmin {
            name: machine.name,
            ip,
            nickname: machine.nickname,
        };
        let _ = MutationCore::edit_machine(&state.conn, machine.id, &form).await;
    } else {
        let form = MachineCreateAdmin {
            name: machine_create.name.to_string(),
            ip,
            nickname: "XXX".to_string(),
        };
        let _ = MutationCore::create_machine(&state.conn, &form).await;
    }

    if let Ok(Some(machine)) =
        QueryCore::find_machine_by_name(&state.conn, &machine_create.name).await
    {
        res = json!(machine);
        status = StatusCode::CREATED;
    }

    (status, Json(res))
}

pub async fn list_machines(State(state): State<Arc<AppState>>) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(machines) = QueryCore::find_machines(&state.conn).await {
        let mut outputs = vec![];
        for m in machines {
            outputs.push(MachinePublic::from(m));
        }
        res = json!(outputs);
        status = StatusCode::OK;
    }
    (status, Json(res))
}

pub async fn get_machine_by_mid(
    State(state): State<Arc<AppState>>,
    Path(mid): Path<i32>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        let m = MachinePublic::from(machine);
        let mut m = MachineTargetsPublic::from(m);
        if let Ok(targets) = QueryCore::find_targets(&state.conn).await {
            let mut outputs = vec![];
            for t in targets {
                outputs.push(TargetPublic::from(t));
            }
            m.targets = outputs;
        }
        res = json!(m);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn create_machine_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Valid(Json(machine_create)): Valid<Json<MachineCreateAdmin>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(_)) = QueryCore::find_machine_by_name(&state.conn, &machine_create.name).await {
        status = StatusCode::CONFLICT;
        res = json!({"msg": "already exists"});
    } else {
        match MutationCore::create_machine(&state.conn, &machine_create).await {
            Ok(_) => {
                status = StatusCode::CREATED;
                res = json!({"msg": "success"});
            }
            Err(_) => {}
        }
    }

    (status, Json(res))
}

pub async fn edit_machine_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(mid): Path<i32>,
    Valid(Json(machine_create)): Valid<Json<MachineCreateAdmin>>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        let _ = MutationCore::edit_machine(&state.conn, machine.id, &machine_create).await;
        res = json!({"msg": "success"});
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn list_machines_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(machines) = QueryCore::find_machines(&state.conn).await {
        res = json!(machines);
        status = StatusCode::OK;
    }
    (status, Json(res))
}

pub async fn get_machine_by_mid_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(mid): Path<i32>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        res = json!(machine);
        status = StatusCode::OK;
    }

    (status, Json(res))
}

pub async fn delete_machine_by_mid_admin(
    State(state): State<Arc<AppState>>,
    _: AdminUser,
    Path(mid): Path<i32>,
) -> (StatusCode, Json<Value>) {
    let mut res = json!({"msg": "failed"});
    let mut status = StatusCode::INTERNAL_SERVER_ERROR;

    if let Ok(Some(machine)) = QueryCore::find_machine_by_id(&state.conn, mid).await {
        let _ = MutationCore::delete_machine(&state.conn, machine.id).await;
        res = json!({"msg": "success"});
        status = StatusCode::OK;
    }

    (status, Json(res))
}
