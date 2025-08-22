pub use sea_orm_migration::prelude::*;

mod m20241030_000001_create_machine;
mod m20241030_000002_create_target;
mod m20241030_000003_create_ping;
mod m20250812_134214_modify_ping;
mod m20250820_074013_add_updated;
mod m20250822_124135_add_key;



pub struct Migrator;

#[async_trait::async_trait]
impl MigratorTrait for Migrator {
    fn migrations() -> Vec<Box<dyn MigrationTrait>> {
        vec![
            Box::new(m20241030_000001_create_machine::Migration),
            Box::new(m20241030_000002_create_target::Migration),
            Box::new(m20241030_000003_create_ping::Migration),
            Box::new(m20250812_134214_modify_ping::Migration),
            Box::new(m20250820_074013_add_updated::Migration),
            Box::new(m20250822_124135_add_key::Migration),
        ]
    }
}
