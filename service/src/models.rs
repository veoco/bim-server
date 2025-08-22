use serde::{Deserialize, Serialize};

use ::entity::{machine::Model as Machine, target::Model as Target};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MachinePublic {
    pub id: i32,
    pub name: String,
    pub ip: String,
    pub created: u64,
    pub updated: Option<u64>,
}

impl From<Machine> for MachinePublic {
    fn from(m: Machine) -> Self {
        let ipv4 = m.ip.contains(".");
        let ip = if ipv4 {
            let parts: Vec<&str> = m.ip.split(".").collect();
            format!("{}.{}.*.*", parts[0], parts[1])
        } else {
            let parts: Vec<&str> = m.ip.split(":").collect();
            let prefix = match parts.len() {
                n if n > 4 => parts[..(n - 4)].join(":"),
                n if n > 1 => parts[..(n - 1)].join(":"),
                _ => m.ip.to_string(),
            };
            format!("{}::*", prefix)
        };

        Self {
            id: m.id,
            name: m.name,
            ip: ip,
            created: m.created.and_utc().timestamp() as u64,
            updated: m.updated.map(|dt| dt.and_utc().timestamp() as u64),
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TargetPublic {
    pub id: i32,
    pub name: String,
    pub created: u64,
    pub updated: Option<u64>,
}

impl From<Target> for TargetPublic {
    fn from(t: Target) -> Self {
        Self {
            id: t.id,
            name: t.name,
            created: t.created.and_utc().timestamp() as u64,
            updated: t.updated.map(|dt| dt.and_utc().timestamp() as u64),
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MachineTargetsPublic {
    pub id: i32,
    pub name: String,
    pub ip: String,
    pub created: u64,
    pub targets: Vec<TargetPublic>,
}

impl From<MachinePublic> for MachineTargetsPublic {
    fn from(m: MachinePublic) -> Self {
        Self {
            id: m.id,
            name: m.name,
            ip: m.ip,
            created: m.created,
            targets: vec![],
        }
    }
}
