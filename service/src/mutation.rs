use std::time::Duration;

use chrono::prelude::*;
use sea_orm::*;

use ::entity::{
    machine, machine::Entity as Machine, ping, ping::Entity as Ping, target,
    target::Entity as Target,
};

use crate::forms::*;

pub struct Mutation;

impl Mutation {
    pub async fn create_machine(
        db: &DbConn,
        form: &MachineCreateAdmin,
    ) -> Result<machine::ActiveModel, DbErr> {
        let now = Utc::now().naive_utc();

        let machine = machine::ActiveModel {
            name: Set(form.name.to_string()),
            ip: Set(form.ip.to_string()),
            nickname: Set(form.nickname.to_string()),
            created: Set(now),
            ..Default::default()
        }
        .save(db)
        .await?;
        Ok(machine)
    }

    pub async fn edit_machine(
        db: &DbConn,
        id: i32,
        form: &MachineCreateAdmin,
    ) -> Result<machine::Model, DbErr> {
        let now = Utc::now().naive_utc();

        machine::ActiveModel {
            id: Set(id),
            name: Set(form.name.to_string()),
            ip: Set(form.ip.to_string()),
            created: Set(now),
            nickname: Set(form.nickname.to_string()),
            ..Default::default()
        }
        .update(db)
        .await
    }

    pub async fn delete_machine(db: &DbConn, id: i32) -> Result<DeleteResult, DbErr> {
        Machine::delete_by_id(id).exec(db).await
    }

    pub async fn create_target(
        db: &DbConn,
        form: &TargetCreateAdmin,
    ) -> Result<target::ActiveModel, DbErr> {
        let now = Utc::now().naive_utc();

        let target = target::ActiveModel {
            name: Set(form.name.to_string()),
            domain: Set(form.domain.clone()),
            ipv4: Set(form.ipv4.clone()),
            ipv6: Set(form.ipv6.clone()),
            created: Set(now),
            ..Default::default()
        }
        .save(db)
        .await?;
        Ok(target)
    }

    pub async fn edit_target(
        db: &DbConn,
        id: i32,
        form: &TargetCreateAdmin,
    ) -> Result<target::Model, DbErr> {
        target::ActiveModel {
            id: Set(id),
            name: Set(form.name.to_string()),
            domain: Set(form.domain.clone()),
            ipv4: Set(form.ipv4.clone()),
            ipv6: Set(form.ipv6.clone()),
            ..Default::default()
        }
        .update(db)
        .await
    }

    pub async fn delete_target(db: &DbConn, id: i32) -> Result<DeleteResult, DbErr> {
        Target::delete_by_id(id).exec(db).await
    }

    pub async fn create_ping(
        db: &DbConn,
        ping_create: PingCreate,
        mid: i32,
        tid: i32,
    ) -> Result<ping::ActiveModel, DbErr> {
        let now = Utc::now().naive_utc();
        let ping = ping::ActiveModel {
            machine_id: Set(mid),
            target_id: Set(tid),
            ipv6: Set(ping_create.ipv6),
            created: Set(now),
            min: Set(ping_create.min as i32),
            avg: Set(ping_create.avg as i32),
            fail: Set(ping_create.fail as i32),
            ..Default::default()
        }
        .save(db)
        .await?;
        Ok(ping)
    }

    pub async fn delete_expire_pings(db: &DbConn) -> Result<DeleteResult, DbErr> {
        Ping::delete_many()
            .filter(
                ping::Column::Created
                    .lt(Utc::now().naive_utc() - Duration::from_secs(7 * 24 * 3600)),
            )
            .exec(db)
            .await
    }
}
