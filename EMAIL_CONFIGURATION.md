# Transactional email with Resend

The API sends registration-confirmation and password-reset messages using Django's
SMTP backend. Resend can be used without adding an application dependency.

## 1. Verify the sending domain in Resend

In the Resend dashboard, add the domain that will appear after `@` in
`DEFAULT_FROM_EMAIL` (for example, `balamukundam.com`). Resend will display the
exact DNS records for that domain. In Cloudflare DNS, create every record shown
there with the displayed type, name, and value:

- DKIM records must be **DNS only** (grey cloud), never proxied.
- Add the SPF record only if there is not already an SPF TXT record at the same
  hostname. SPF must be a single TXT record; merge any existing provider values
  into it rather than creating a second SPF record.
- Add a DMARC TXT record if Resend offers one and you do not already manage
  DMARC. Start with a monitoring policy (`p=none`) before enforcing it.

Return to Resend and wait for the domain to show as verified. Use the exact
record values from its dashboard; DKIM selectors are specific to your account.

## 2. Add the Resend credentials

Put this configuration in the deployment's secret store or the ignored project
`.env` file. Replace the password with the Resend API key; do not add it to
`.env.example`, source control, or the frontend.

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.resend.com
EMAIL_PORT=587
EMAIL_HOST_USER=resend
EMAIL_HOST_PASSWORD=re_replace_with_your_resend_api_key
EMAIL_USE_TLS=true
EMAIL_USE_SSL=false
DEFAULT_FROM_EMAIL=Balamukundam Vidyalayam <noreply@your-verified-domain.com>
FRONTEND_BASE_URL=https://your-application-domain.com
```

This uses Resend's STARTTLS connection on port 587. If the hosting network blocks
that port, use port 465 instead and set `EMAIL_USE_TLS=false` plus
`EMAIL_USE_SSL=true`.

## 3. Restart and test

Restart the API deployment after supplying the environment values. Then use the
application's resend-confirmation or password-reset flow and check the Resend
email logs. A message sent from an unverified domain will not be deliverable.
