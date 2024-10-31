use std::time::Duration;

use ::entity::{
    machine, machine::Entity as Machine, ping, ping::Entity as Ping, target,
    target::Entity as Target,
};
use chrono::prelude::*;
use sea_orm::*;

pub struct Query;

impl Query {
    pub async fn find_machine_by_name(
        db: &DbConn,
        name: &str,
    ) -> Result<Option<machine::Model>, DbErr> {
        Machine::find()
            .filter(machine::Column::Name.eq(name))
            .one(db)
            .await
    }

    pub async fn find_machines(db: &DbConn) -> Result<Vec<machine::Model>, DbErr> {
        Machine::find()
            .order_by_asc(machine::Column::Id)
            .all(db)
            .await
    }

    pub async fn find_machine_by_id(db: &DbConn, id: i32) -> Result<Option<machine::Model>, DbErr> {
        Machine::find_by_id(id).one(db).await
    }

    pub async fn find_targets(db: &DbConn) -> Result<Vec<target::Model>, DbErr> {
        Target::find()
            .order_by_asc(target::Column::Id)
            .all(db)
            .await
    }

    pub async fn find_target_by_id(db: &DbConn, id: i32) -> Result<Option<target::Model>, DbErr> {
        Target::find_by_id(id).one(db).await
    }

    pub async fn find_target_by_name(
        db: &DbConn,
        name: &str,
    ) -> Result<Option<target::Model>, DbErr> {
        Target::find()
            .filter(target::Column::Name.eq(name))
            .one(db)
            .await
    }

    pub async fn find_pings_by_machine_id_and_target_id(
        db: &DbConn,
        mid: i32,
        tid: i32,
        delta: &str,
        ipv6: bool,
    ) -> Result<Vec<ping::Model>, DbErr> {
        let time_delta = if delta == "7d" {
            Duration::from_secs(7 * 24 * 3600)
        } else {
            Duration::from_secs(24 * 3600)
        };

        Ping::find()
            .filter(ping::Column::MachineId.eq(mid))
            .filter(ping::Column::TargetId.eq(tid))
            .filter(ping::Column::Ipv6.eq(ipv6))
            .filter(ping::Column::Created.gt(Utc::now().naive_utc() - time_delta))
            .order_by_asc(ping::Column::Created)
            .all(db)
            .await
    }
}
