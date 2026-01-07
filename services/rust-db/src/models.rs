use serde::Serialize;

#[derive(Debug, Serialize)]
pub struct KeyInfo {
    pub key: String,
    pub mime_type: String,
}

#[derive(Debug)]
pub struct Entry {
    pub mime_type: String,
    pub content: Vec<u8>,
}
