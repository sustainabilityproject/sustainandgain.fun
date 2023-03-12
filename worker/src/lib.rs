use sqlx::PgPool;

use crate::notifications::{get_notifications, send_notifications};

pub mod notifications;
pub mod mail;

pub async fn run(pool: &PgPool) {
    println!("Running background worker");

    send_notifications(pool, get_notifications(pool).await).await;
}

