use serde::{Deserialize, Serialize};

use ::entity::{machine::Model as Machine, ping::Model as Ping, target::Model as Target};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MachinePublic {
    pub id: i32,
    pub ip: String,
    pub nickname: String,
    pub created: String,
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
            nickname: m.nickname,
            ip: ip,
            created: m.created.to_string(),
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct TargetPublic {
    pub id: i32,
    pub name: String,
    pub created: String,
}

impl From<Target> for TargetPublic {
    fn from(t: Target) -> Self {
        Self {
            id: t.id,
            name: t.name,
            created: t.created.to_string(),
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct MachineTargetsPublic {
    pub id: i32,
    pub ip: String,
    pub nickname: String,
    pub created: String,
    pub targets: Vec<TargetPublic>,
}

impl From<MachinePublic> for MachineTargetsPublic {
    fn from(m: MachinePublic) -> Self {
        Self {
            id: m.id,
            ip: m.ip,
            nickname: m.nickname,
            created: m.created,
            targets: vec![],
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct PingPublic {
    pub created: i64,
    pub min: f32,
    pub jitter: f32,
    pub failed: i32,
}

impl From<Ping> for PingPublic {
    fn from(p: Ping) -> Self {
        Self {
            created: p.created.and_utc().timestamp(),
            min: p.min,
            jitter: p.jitter,
            failed: p.failed,
        }
    }
}
