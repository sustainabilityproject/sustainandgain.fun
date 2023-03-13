use std::sync::Arc;
use std::time::Duration;
use clokwerk::{Job, Scheduler, TimeUnits};
use sqlx::PgPool;
use crate::notifications::{get_notifications, send_notifications};

pub fn schedule(pool: PgPool) {
    let pool = Arc::new(pool);
    let mut scheduler = Scheduler::new();

    scheduler.every(1.day()).at("12:00").run({
        let pool = pool;
        move || {
            let pool = pool.clone();
            tokio::spawn(async move {
                // Fetch the latest notifications
                let notifications = get_notifications(&pool).await;

                // Send the notifications
                if let Err(e) = send_notifications(&pool, notifications).await {
                    eprintln!("Failed to send notifications: {}", e);
                }
            });
        }
    });

    loop {
        // Run the scheduler in a loop
        scheduler.run_pending();
        std::thread::sleep(Duration::from_millis(600000));
    }
}