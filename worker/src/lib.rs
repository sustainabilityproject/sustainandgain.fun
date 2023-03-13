use sqlx::PgPool;
use crate::bomb_task::process_bomb_tasks;

use crate::schedule::schedule;

pub mod notifications;
pub mod mail;
pub mod bomb_task;
pub mod schedule;

/// Run the background worker
pub async fn run(pool: &PgPool) {
    println!("Running background worker");

    process_bomb_tasks(pool).await;
    // Schedule the background worker
    schedule(pool.clone());
}

