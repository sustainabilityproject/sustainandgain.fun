use sqlx::PgPool;

use crate::schedule::schedule;

pub mod notifications;
pub mod mail;
pub mod bomb_task;
pub mod schedule;

/// Run the background worker
pub async fn run(pool: &PgPool) {
    println!("Running background worker");

    // Send an email notifying that the app has been deployed
    mail::send_deployed_email().await;

    // Schedule the background worker
    schedule(pool.clone());
}

