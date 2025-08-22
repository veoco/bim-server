use sea_orm_migration::prelude::*;

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .alter_table(
                Table::alter()
                    .table(Machine::Table)
                    .add_column(
                        ColumnDef::new(Machine::Key)
                            .string()
                            .not_null()
                            .default("default_key"),
                    )
                    .to_owned(),
            )
            .await?;
        manager
            .alter_table(
                Table::alter()
                    .table(Machine::Table)
                    .drop_column(Machine::Nickname)
                    .to_owned(),
            )
            .await?;
        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Machine::Key).to_owned())
            .await?;
        manager
            .alter_table(
                Table::alter()
                    .table(Machine::Table)
                    .add_column(
                        ColumnDef::new(Machine::Nickname)
                            .string()
                            .not_null()
                            .default("XXX"),
                    )
                    .to_owned(),
            )
            .await?;
        Ok(())
    }
}

#[derive(DeriveIden)]
enum Machine {
    Table,
    Key,
    Nickname,
}
