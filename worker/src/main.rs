use std::env;

use dotenv::dotenv;
use sqlx::PgPool;

use worker::run;

#[tokio::main]
async fn main() {
    // Load the environment variables
    dotenv().ok();

    // Connect to the database
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    let pool = PgPool::connect(&db_url).await.expect("Failed to connect to Postgres");

    // Run the background worker
    run(&pool).await;
}
