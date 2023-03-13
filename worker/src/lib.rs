use sqlx::PgPool;
use crate::schedule::schedule;

mod notifications;
mod mail;
pub mod schedule;

pub async fn run(pool: &PgPool) {
    println!("Running background worker");

    schedule(pool.clone());
}

