use std::sync::Arc;

use axum::{
    async_trait,
    extract::{FromRef, FromRequestParts},
    http::{request::Parts, StatusCode},
    Json, RequestPartsExt,
};
use axum_extra::{
    headers::{authorization::Bearer, Authorization},
    TypedHeader,
};
use serde_json::{json, Value};

use crate::AppState;

pub struct AdminUser {}

#[async_trait]
impl<S> FromRequestParts<S> for AdminUser
where
    Arc<AppState>: FromRef<S>,
    S: Send + Sync,
{
    type Rejection = (StatusCode, Json<Value>);

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let s = Arc::from_ref(state);
        if let Ok(TypedHeader(Authorization(bearer))) =
            parts.extract::<TypedHeader<Authorization<Bearer>>>().await
        {
            let token = bearer.token();
            if token == s.admin_password {
                return Ok(Self {});
            }
        }
        Err((
            StatusCode::UNAUTHORIZED,
            Json(json!({"msg": "Login required"})),
        ))
    }
}

pub struct ApiClient {}

#[async_trait]
impl<S> FromRequestParts<S> for ApiClient
where
    Arc<AppState>: FromRef<S>,
    S: Send + Sync,
{
    type Rejection = (StatusCode, Json<Value>);

    async fn from_request_parts(parts: &mut Parts, state: &S) -> Result<Self, Self::Rejection> {
        let s = Arc::from_ref(state);
        if let Ok(TypedHeader(Authorization(bearer))) =
            parts.extract::<TypedHeader<Authorization<Bearer>>>().await
        {
            let token = bearer.token();
            if token == s.api_token {
                return Ok(Self {});
            }
        }
        Err((
            StatusCode::UNAUTHORIZED,
            Json(json!({"msg": "Api token required"})),
        ))
    }
}
