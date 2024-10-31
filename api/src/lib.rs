use std::sync::Arc;
use std::{env, net::SocketAddr};

use axum::extract::{Request, State};
use axum::response::IntoResponse;
use axum::{
    http::StatusCode,
    routing::{get, post},
    Router,
};
use migration::{Migrator, MigratorTrait};
use tokio::net::TcpListener;
use tokio::signal;
use tokio::time::interval;
use tower::ServiceExt;
use tower_http::services::{ServeDir, ServeFile};
use tracing::info;
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

use server_service::sea_orm::{ConnectOptions, Database, DatabaseConnection};
use server_service::Mutation as MutationCore;

mod extractors;
mod machines;
mod pings;
mod targets;
use machines::{
    create_machine_admin, create_machine_client, delete_machine_by_mid_admin, edit_machine_admin,
    get_machine_by_mid, get_machine_by_mid_admin, list_machines, list_machines_admin,
};
use pings::{create_ping_client, list_pings};
use targets::{
    create_target_admin, delete_target_admin, edit_target_admin, get_target_by_tid_admin,
    list_targets_admin, list_targets_client,
};

#[derive(Clone)]
pub struct AppState {
    conn: DatabaseConnection,
    admin_password: String,
    api_token: String,
    static_root: String,
}

async fn shutdown_signal() {
    let ctrl_c = async {
        signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        signal::unix::signal(signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {},
        _ = terminate => {},
    }

    info!("signal received, starting graceful shutdown");
}

async fn clean_database(state: Arc<AppState>) {
    let mut it = interval(std::time::Duration::from_secs(300));

    loop {
        it.tick().await;
        let _ = MutationCore::delete_expire_pings(&state.conn).await;
    }
}

async fn server_index(State(state): State<Arc<AppState>>, request: Request) -> impl IntoResponse {
    let path = format!("{}/index.html", state.static_root);
    match ServeFile::new(path).oneshot(request).await {
        Ok(res) => res.into_response(),
        Err(_) => (StatusCode::NOT_FOUND, "Not Found").into_response(),
    }
}

fn build_app(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/api/machines/", get(list_machines))
        .route("/api/machines/:mid", get(get_machine_by_mid))
        .route("/api/machines/:mid/targets/:tid/:delta", get(list_pings))
        .route("/api/client/targets/", get(list_targets_client))
        .route("/api/client/machines/", post(create_machine_client))
        .route(
            "/api/client/machines/:mid/targets/:tid",
            post(create_ping_client),
        )
        .route(
            "/api/admin/machines/",
            post(create_machine_admin).get(list_machines_admin),
        )
        .route(
            "/api/admin/machines/:mid",
            get(get_machine_by_mid_admin)
                .post(edit_machine_admin)
                .delete(delete_machine_by_mid_admin),
        )
        .route(
            "/api/admin/targets/",
            post(create_target_admin).get(list_targets_admin),
        )
        .route(
            "/api/admin/targets/:tid",
            get(get_target_by_tid_admin)
                .post(edit_target_admin)
                .delete(delete_target_admin),
        )
        .route("/m/", get(server_index))
        .route("/m/:mid", get(server_index))
        .route("/admin/", get(server_index))
        .route("/admin/login", get(server_index))
        .nest_service("", ServeDir::new(state.static_root.clone()))
        .with_state(state)
}

#[tokio::main]
async fn start() -> anyhow::Result<()> {
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| {
                format!("{}=debug,tower_http=debug", env!("CARGO_CRATE_NAME")).into()
            }),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    dotenvy::dotenv().ok();
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL is not set in .env file");
    let addr = env::var("LISTEN_ADDRESS").unwrap_or(String::from("127.0.0.1:3000"));
    let admin_password = env::var("ADMIN_PASSWORD").unwrap_or(String::from("fake-admin-password"));
    let api_token = env::var("API_TOKEN").unwrap_or(String::from("fake-token"));
    let static_root = env::var("STATIC_ROOT").unwrap_or(String::from("./static"));

    info!("Listening on http://{addr}/");

    let opt = ConnectOptions::new(db_url.clone());
    let conn = Database::connect(opt)
        .await
        .expect("Database connection failed");
    Migrator::up(&conn, None).await.unwrap();

    let state = Arc::new(AppState {
        conn,
        admin_password,
        api_token,
        static_root,
    });

    tokio::spawn(clean_database(state.clone()));

    let app = build_app(state);

    let listener = TcpListener::bind(addr).await?;

    axum::serve(
        listener,
        app.into_make_service_with_connect_info::<SocketAddr>(),
    )
    .with_graceful_shutdown(shutdown_signal())
    .await?;

    Ok(())
}

pub fn main() {
    let result = start();

    if let Some(err) = result.err() {
        println!("Error: {err}");
    }
}
