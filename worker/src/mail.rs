use lettre::{
    transport::smtp::authentication::Credentials, Message, AsyncSmtpTransport, Tokio1Executor, AsyncTransport,
};

pub async fn send_mail(
    from: &str,
    to: &str,
    subject: &str,
    body: String,
) -> Result<(), Box<dyn std::error::Error>> {
    let email_host = std::env::var("EMAIL_HOST")?;
    let email_port = std::env::var("EMAIL_PORT")?;
    let email_use_tls = std::env::var("EMAIL_USE_TLS")?;
    let username = std::env::var("EMAIL_HOST_USER")?;
    let password = std::env::var("EMAIL_HOST_PASSWORD")?;

    let smtp_credentials = Credentials::new(username, password);

    let mailer = match email_use_tls.as_str() {
        "True" => AsyncSmtpTransport::<Tokio1Executor>::starttls_relay(&email_host)
            .unwrap()
            .credentials(smtp_credentials)
            .port(email_port.parse::<u16>()?)
            .build(),
        // Don't use any kind of TLS or SSL
        "False" => AsyncSmtpTransport::<Tokio1Executor>::builder_dangerous(&email_host)
            .credentials(smtp_credentials)
            .port(email_port.parse::<u16>()?)
            .build(),
        _ => AsyncSmtpTransport::<Tokio1Executor>::relay(&email_host)
            .unwrap()
            .credentials(smtp_credentials)
            .port(email_port.parse::<u16>()?)
            .build(),
    };
    let email = Message::builder()
        .from(from.parse()?)
        .to(to.parse()?)
        .subject(subject)
        .body(body)?;

    let result = mailer.send(email).await?;
    println!("Email sent: {:?}", result);
    Ok(())
}