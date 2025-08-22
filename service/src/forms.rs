use serde::Deserialize;
use validator::Validate;

#[derive(Debug, Validate, Deserialize)]
pub struct PingCreate {
    pub ipv6: bool,
    #[validate(range(max = 1000))]
    pub min: u16,
    #[validate(range(max = 1000))]
    pub avg: u16,
    #[validate(range(max = 20))]
    pub fail: u8,
}

#[derive(Debug, Validate, Deserialize)]
pub struct PingFilter {
    pub ipv6: Option<bool>,
}

#[derive(Debug, Validate, Deserialize)]
pub struct MachineCreateAdmin {
    pub name: String,
    pub ip: String,
    pub key: String,
}

#[derive(Debug, Validate, Deserialize)]
pub struct TargetCreateAdmin {
    pub name: String,
    pub domain: Option<String>,
    pub ipv4: Option<String>,
    pub ipv6: Option<String>,
}
