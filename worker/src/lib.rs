use sqlx::PgPool;

use crate::schedule::schedule;

pub mod notifications;
pub mod mail;
pub mod bomb_task;
pub mod schedule;

/// Run the background worker
pub async fn run(pool: &PgPool) {
    println!("Running background worker");

    // Schedule the background worker
    schedule(pool.clone());
}

