use std::collections::HashMap;

use maud::html;
use serde::Deserialize;
use sqlx::PgPool;
use sqlx::types::Json;

use crate::mail;

/// Notification is a representation of a notification in the database
#[derive(Debug, Deserialize, Clone)]
pub struct Notification {
    pub id: i32,
    pub actor_object_id: String,
    pub actor_content_type_id: i32,
    pub verb: String,
    pub recipient_id: i64,
    pub data: Option<Json<serde_json::Value>>,
    pub recipient_username: String,
    pub recipient_email: String,
    pub actor_username: String,
}


impl Notification {
    /// HTML returns the HTML representation of the notification
    fn html(&self) -> maud::Markup {
        html! {
            li {
                p { (self.actor_username) " " (self.verb) }
                p {
                    a href=(
                        self.data.as_ref()
                            .and_then(|data| serde_json::from_value::<NotificationData>(data.0.clone()).ok())
                            .and_then(|notification_data| notification_data.url.map(|url| format!("https://www.sustainandgain.fun{}", url)))
                            .unwrap_or_else(|| "https://sustainandgain.fun/".to_string())
                    ) {
                        "View"
                    }
                }
            }
        }
    }

    /// Body returns the plain text representation of the notification
    fn body(&self, intro: &str) -> String {
        format!("{} You can view them at https://www.sustainandgain.fun/. Sustainability Steve", intro)
    }
}


/// NotificationData is the data associated with a notification which contains the URL to the notification
#[derive(Debug, Deserialize)]
pub struct NotificationData {
    pub url: Option<String>,
}

/// get_notifications returns all notifications that have not yet been emailed
///
/// ```
/// use sqlx::PgPool;
/// use worker::notifications::get_notifications;
///
/// async fn run(pool: &PgPool) {
///    let notifications = get_notifications(pool).await;
///
///   for notification in notifications {
///      println!("{:?}", notification);
///  }
/// }
/// ```
pub async fn get_notifications(pool: &PgPool) -> Vec<Notification> {
    let notifications: Vec<Notification> = sqlx::query_as!(
        Notification,
        r#"
        SELECT
            n.id,
            n.actor_object_id,
            n.actor_content_type_id,
            n.verb,
            n.recipient_id,
            n.data as "data: Json<serde_json::Value>",
            r.username as recipient_username,
            r.email as recipient_email,
            a.username as actor_username
        FROM notifications_notification n
        INNER JOIN accounts_user a ON n.actor_object_id = a.id::text
        INNER JOIN accounts_user r ON n.recipient_id = r.id
        WHERE n.emailed = false AND r.email IS NOT NULL
        "#,
    )
        .fetch_all(pool)
        .await
        .expect("Failed to fetch notifications")
        .into_iter()
        .map(|n| {
            let data = match n.data {
                Some(data) => Some(serde_json::from_value(data.0).unwrap()),
                None => None,
            };
            Notification {
                data,
                ..n
            }
        })
        .collect();

    notifications
}

/// send_notifications sends the given notifications and marks them as emailed
///
/// ```
/// use sqlx::PgPool;
/// use worker::notifications::{get_notifications, send_notifications};
///
/// async fn run(pool: &PgPool) {
///    let notifications = get_notifications(pool).await;
///    if let Err(e) = send_notifications(&pool, notifications).await {
///         eprintln!("Failed to send notifications: {}", e);
///    }
/// }
/// ```
pub async fn send_notifications(pool: &PgPool, notifications: Vec<Notification>) -> Result<(), Box<dyn std::error::Error>> {
    let from = "Sustainability Steve <steve@sustainandgain.fun>";
    let subject = "[Sustain and Gain] You have new notifications";

    // Group the notifications by user
    let mut user_notifications: HashMap<String, Vec<Notification>> = HashMap::new();
    for n in notifications.clone() {
        user_notifications.entry(n.recipient_email.clone()).or_insert_with(Vec::new).push(n);
    }

    // For each user, send them an email with all of their notifications
    for n in &user_notifications {
        println!("Sending notification: {:?}", n);
        let to = n.0.as_str();
        let intro = format!("Hello {}! You have new notifications.", n.1[0].recipient_username);
        let body = n.1[0].body(&intro);
        let html = html! {
            div {
                h2 { (intro) }
                @for notification_group in user_notifications.values() {
                    ul {
                        @for notification in notification_group {
                            (notification.html())
                        }
                    }
                }
                p { "Looking forward to seeing you on the site!"}
                h3 { "Sustainability Steve" }
            }
        };
        mail::send_mail(from, to, subject, html, body).await?;
    }

    // Mark the notifications as emailed
    for n in notifications {
        sqlx::query!(
            r#"
            UPDATE notifications_notification
            SET emailed = true
            WHERE id = $1
            "#,
            n.id
        )
            .execute(pool)
            .await
            .expect("Failed to update notification");
    }

    Ok(())
}