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

pub async fn send_notifications(pool: &PgPool, notifications: Vec<Notification>) {
    let from = "Sustainability Steve <steve@sustainandgain.fun>";
    let subject = "You have a new notification";

    for n in notifications {
        println!("Sending notification: {:?}", n);
        let url = match &n.data {
            Some(data) => match serde_json::from_value::<NotificationData>(data.0.clone()) {
                Ok(notification_data) => match notification_data.url {
                    Some(url) => format!("https://sustainandgain.fun{}", url),
                    None => "https://sustainandgain.fun/".to_string(),
                },
                Err(_) => "https://sustainandgain.fun/".to_string(),
            },
            None => "https://sustainandgain.fun/".to_string(),
        };
        let to = &n.recipient_email;
        let body = format!(
            "<h1>Notification</h1>
            <p>{} {}</p>
            <p>{}</p>",
            n.actor_username, n.verb, url
        );
        mail::send_mail(from, to, subject, body).await?;
    }

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