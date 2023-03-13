use std::sync::Arc;
use std::time::Duration;

use clokwerk::{Job, Scheduler, TimeUnits};
use sqlx::PgPool;

use crate::notifications::{get_notifications, send_notifications};

/// Schedules the background worker
///
/// ```
/// use sqlx::PgPool;
/// use worker::schedule::schedule;
/// use dotenv::dotenv;
/// use std::env;
///
/// #[tokio::main]
/// async fn main() {
///     dotenv().ok();
///     let db_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
///     let pool = PgPool::connect(db_url.as_str()).await.unwrap();
///     schedule(pool); // This will run forever as it constantly checks for new notifications
/// }
/// ```
pub fn schedule(pool: PgPool) {
    let pool = Arc::new(pool);
    let mut scheduler = Scheduler::new();

    // Schedule the background worker to run every day at 14:25 and send notifications
    scheduler.every(1.day()).at("14:25").run({
        let pool = pool.clone();
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

    // Schedule the background worker to run every hour and process bomb tasks
    scheduler.every(1.hour()).run({
        let pool = pool;
        move || {
            let pool = pool.clone();
            tokio::spawn(async move {
                // Process bomb tasks
                if let Err(e) = crate::bomb_task::process_bomb_tasks(&pool).await {
                    eprintln!("Failed to process bomb tasks: {}", e);
                }
            });
        }
    });

    loop {
        // Run the scheduler in a loop
        scheduler.run_pending();
        // Sleep for 1 second
        std::thread::sleep(Duration::from_millis(1000));
    }
}