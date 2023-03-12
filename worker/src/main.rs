use std::env;

use dotenv::dotenv;
use sqlx::PgPool;

use worker::run;

#[tokio::main]
async fn main() {
    dotenv().ok();
    // let debug = env::var("DEBUG").unwrap_or("0".to_string()) == "1";
    let db_url = env::var("DATABASE_URL").expect("DATABASE_URL must be set");
    // connect to postgres
    let pool = PgPool::connect(&db_url).await.expect("Failed to connect to Postgres");
    run(&pool).await;
}
