use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(Machine::Table)
                    .if_not_exists()
                    .col(pk_auto(Machine::Id))
                    .col(string_uniq(Machine::Name))
                    .col(string(Machine::Ip))
                    .col(string(Machine::Nickname))
                    .col(date_time(Machine::Created))
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Machine::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Machine {
    Table,
    Id,
    Name,
    Ip,
    Nickname,
    Created,
}
