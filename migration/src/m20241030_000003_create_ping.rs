use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(Ping::Table)
                    .if_not_exists()
                    .col(pk_auto(Ping::Id))
                    .col(integer(Ping::MachineId))
                    .col(integer(Ping::TargetId))
                    .col(boolean(Ping::Ipv6))
                    .col(date_time(Ping::Created))
                    .col(float(Ping::Min))
                    .col(float(Ping::Jitter))
                    .col(integer(Ping::Failed))
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-ping-machine")
                            .from(Ping::Table, Ping::MachineId)
                            .to(Machine::Table, Machine::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .foreign_key(
                        ForeignKey::create()
                            .name("fk-ping-target")
                            .from(Ping::Table, Ping::TargetId)
                            .to(Target::Table, Target::Id)
                            .on_delete(ForeignKeyAction::Cascade)
                            .on_update(ForeignKeyAction::Cascade),
                    )
                    .to_owned(),
            )
            .await?;

        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Ping::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Ping {
    Table,
    Id,
    MachineId,
    TargetId,
    Ipv6,
    Created,
    Min,
    Jitter,
    Failed,
}

#[derive(DeriveIden)]
enum Target {
    Table,
    Id,
}

#[derive(DeriveIden)]
enum Machine {
    Table,
    Id,
}
