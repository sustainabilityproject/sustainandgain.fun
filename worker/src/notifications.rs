use std::collections::HashMap;

use maud::html;
use serde::Deserialize;
use sqlx::PgPool;
use sqlx::types::Json;

use crate::mail;

#[derive(Debug, Deserialize)]
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
    pub actor_email: String,
}

#[derive(Debug, Deserialize)]
pub struct NotificationData {
    pub url: Option<String>,
}

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
            a.username as actor_username,
            a.email as actor_email
        FROM notifications_notification n
        INNER JOIN accounts_user a ON n.actor_object_id = a.id::text
        INNER JOIN accounts_user r ON n.recipient_id = r.id
        WHERE n.emailed = false
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

pub async fn send_notifications(pool: &PgPool, notifications: Vec<Notification>) -> Result<(), Box<dyn std::error::Error>> {
    let from = "Sustainability Steve <steve@sustainandgain.fun>";
    let subject = "[Sustain and Gain] You have new notifications";

    let mut user_notifications: HashMap<String, Vec<Notification>> = HashMap::new();
    for n in notifications {
        user_notifications.entry(n.recipient_email.clone()).or_insert_with(Vec::new).push(n);
    }

    for n in &user_notifications {
        println!("Sending notification: {:?}", n);
        let to = n.0.as_str();
        let intro = format!("Hello {}! You have new notifications.", n.1[0].recipient_username);
        let body = format!("{} You can view them at https://www.sustainandgain.fun/. Sustainability Steve", intro);
        let html = html! {
            div {
                h2 { (intro) }
                @for notification_group in user_notifications.values() {
                    ul {
                        @for notification in notification_group {
                            li {
                                p { (notification.actor_username) " " (notification.verb) }
                                p {
                                    a href=(
                                        notification.data.as_ref()
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
                }
                p { "Looking forward to seeing you on the site!"}
                h3 { "Sustainability Steve" }
            }
        };
        mail::send_mail(from, to, subject, html, body).await?;
    }

    Ok(())
//     for n in notifications {
//         sqlx::query!(
//             r#"
//             UPDATE notifications_notification
//             SET emailed = true
//             WHERE id = $1
//             "#,
//             n.id
//         )
//         .execute(pool)
//         .await
//         .expect("Failed to update notification");
//     }
}