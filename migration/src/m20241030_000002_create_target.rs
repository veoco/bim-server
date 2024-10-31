use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .create_table(
                Table::create()
                    .table(Target::Table)
                    .if_not_exists()
                    .col(pk_auto(Target::Id))
                    .col(string_uniq(Target::Name))
                    .col(string_null(Target::Domain))
                    .col(string_null(Target::Ipv4))
                    .col(string_null(Target::Ipv6))
                    .col(date_time(Target::Created))
                    .to_owned(),
            )
            .await
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Target::Table).to_owned())
            .await
    }
}

#[derive(DeriveIden)]
enum Target {
    Table,
    Id,
    Name,
    Domain,
    Ipv4,
    Ipv6,
    Created,
}
