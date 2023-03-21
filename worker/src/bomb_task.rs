use std::collections::HashMap;

use chrono::Duration;
use chrono::Utc;
use maud::html;
use sqlx::PgPool;
use sqlx::postgres::types::PgInterval;

use crate::mail;

/// BombTask is a representation of a bomb task in the database
#[derive(Debug)]
pub struct BombTask {
    pub task_title: String,
    pub time_accepted: chrono::DateTime<Utc>,
    pub bomb_time_limit: Option<PgInterval>,
    pub assigned_username: String,
    pub assigned_email: String,
}

// HTML email for bomb task
impl BombTask {
    /// Get the time left before the bomb explodes
    fn time_left(&self) -> Duration {
        let time_limit = self.bomb_time_limit.clone().unwrap();
        let days = time_limit.days;
        let microseconds = time_limit.microseconds;
        let duration = Duration::days(days as i64) + Duration::microseconds(microseconds);
        let expire_time = self.time_accepted + duration;
        expire_time - Utc::now()
    }

    /// Human readable time left for emails
    fn human_readable_time_left(&self) -> String {
        let mut time_left_string = String::new();
        if self.time_left().num_days() > 0 {
            time_left_string.push_str(&format!("{} days ", self.time_left().num_days()));
        }
        if self.time_left().num_hours() > 0 {
            time_left_string.push_str(&format!("{} hours ", self.time_left().num_hours() % 24));
        }
        if self.time_left().num_minutes() > 0 {
            time_left_string.push_str(&format!("{} minutes ", self.time_left().num_minutes() % 60));
        }
        if self.time_left().num_seconds() > 0 {
            time_left_string.push_str(&format!("{} seconds ", self.time_left().num_seconds() % 60));
        }

        if time_left_string.is_empty() {
            return "NOW".to_string();
        }

        format!("in {}", time_left_string)
    }

    /// HTML representation of the notification for emails
    fn html(&self) -> maud::Markup {
        html! {
            li {
                p { (self.task_title) " explodes " (self.human_readable_time_left())"!" }
                p {
                    a href="https://www.sustainandgain.fun/tasks/" {
                        "View"
                    }
                }
            }
        }
    }
}

/// Get all bomb tasks that are active
pub async fn get_bomb_tasks(pool: &PgPool) -> Vec<BombTask> {
    sqlx::query_as!(
        BombTask,
        r#"
        SELECT
            t.title AS task_title,
            ti.time_accepted,
            t.bomb_time_limit,
            u.username AS assigned_username,
            u.email AS assigned_email
        FROM tasks_taskinstance ti
        JOIN tasks_task t ON ti.task_id = t.id
        JOIN friends_profile p ON ti.profile_id = p.id
        JOIN accounts_user u ON p.user_id = u.id
        WHERE t.is_bomb = true AND ti.status = 'ACTIVE'
        "#,
    )
        .fetch_all(pool)
        .await
        .expect("Failed to fetch tasks")
}


/// Process all bomb tasks
pub async fn process_bomb_tasks(pool: &PgPool) -> Result<(), Box<dyn std::error::Error>> {
    let from = "Sustainability Steve <steve@sustainandgain.fun>";
    let subject = "[Sustain and Gain] Tasks are about to expire!";
    let bomb_tasks = get_bomb_tasks(pool).await;

    // Group the bomb tasks which expire in less than 2 hours by email
    let mut bomb_tasks_by_email: HashMap<String, Vec<BombTask>> = HashMap::new();
    for bomb_task in bomb_tasks {
        if bomb_task.time_left() < Duration::hours(2) {
            bomb_tasks_by_email
                .entry(bomb_task.assigned_email.clone())
                .or_insert_with(Vec::new)
                .push(bomb_task);
        }
    }

    // Send an email to each user with their bomb tasks which are about to expire
    for (email, bomb_tasks) in bomb_tasks_by_email {
        let html = html! {
            h2 { "Hi " (bomb_tasks[0].assigned_username)"!" }
            p { "You have " (bomb_tasks.len()) " task(s) that are expiring soon:" }
            ul {
                @for bomb_task in &bomb_tasks {
                    (bomb_task.html())
                }
            }
            p { "Looking forward to seeing you on Sustain and Gain!" }
            h3 { "Sustainability Steve" }
        };
        let body = format!("You have {} task(s) that are expiring soon. You can view them at https://www.sustainandgain.fun/tasks/. Sustainability Steve", bomb_tasks.len());
        mail::send_mail(from, email.as_str(), subject, html, body).await?;

        for bomb_task in bomb_tasks {
            if bomb_task.time_left() < Duration::seconds(0) {
                sqlx::query!(
                    r#"
                    UPDATE tasks_taskinstance
                    SET status = 'EXPLODED'
                    WHERE task_id = (
                        SELECT id FROM tasks_task WHERE title = $1
                    ) AND profile_id = (
                        SELECT id FROM friends_profile WHERE user_id = (
                            SELECT id FROM accounts_user WHERE email = $2
                        )
                    )
                    "#,
                    bomb_task.task_title,
                    bomb_task.assigned_email,
                )
                    .execute(pool)
                    .await
                    .expect("Failed to update task instance");
            }
        }
    }

    Ok(())
}