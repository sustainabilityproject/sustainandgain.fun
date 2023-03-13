use lettre::{
    AsyncSmtpTransport, AsyncTransport, Message, Tokio1Executor, transport::smtp::authentication::Credentials,
};
use lettre::message::{header, MultiPart, SinglePart};

/// Send an email
///
/// ```
/// use worker::mail::send_mail;
///
/// async fn run() {
///     let html = maud::html! {
///         div {
///             h1 { "Hello World!" }
///         }
///     };
///     let body = "Hello World!";
///     let from = "Sustainability Steve <steve@sustainandgain.fun>";
///     let to = "test@test.com";
///     let subject = "Hello World!";
///
///     if let Err(e) = send_mail(from, to, subject, html, body.to_string()).await {
///         eprintln!("Failed to send email: {}", e);
///     }
/// }
/// ```
pub async fn send_mail(
    from: &str,
    to: &str,
    subject: &str,
    html: maud::Markup,
    body: String,
) -> Result<(), Box<dyn std::error::Error>> {
    let email_host = std::env::var("EMAIL_HOST")?;
    let email_port = std::env::var("EMAIL_PORT")?;
    let email_use_tls = std::env::var("EMAIL_USE_TLS")?;
    let username = std::env::var("EMAIL_HOST_USER")?;
    let password = std::env::var("EMAIL_HOST_PASSWORD")?;

    let smtp_credentials = Credentials::new(username, password);

    // In production, we use TLS to encrypt the connection
    // In development, we use a dangerous builder to allow insecure connections
    let mailer = match email_use_tls.as_str() {
        "True" => AsyncSmtpTransport::<Tokio1Executor>::starttls_relay(&email_host)
            .unwrap()
            .credentials(smtp_credentials)
            .port(email_port.parse::<u16>()?)
            .build(),
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

    // Build the email
    let email = Message::builder()
        .from(from.parse()?)
        .to(to.parse()?)
        .subject(subject)
        .multipart(
            MultiPart::alternative()
                .singlepart(
                    SinglePart::builder()
                        .header(header::ContentType::TEXT_PLAIN)
                        .body(body),
                )
                .singlepart(
                    SinglePart::builder()
                        .header(header::ContentType::TEXT_HTML)
                        .body(html.into_string()),
                ),
        )?;

    // Send the email
    let result = mailer.send(email).await?;
    println!("Email sent: {:?}", result);
    Ok(())
}