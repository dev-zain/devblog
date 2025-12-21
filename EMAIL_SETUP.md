# Email Backend Setup Guide

This guide will help you configure email sending for DevBlog.

## Current Configuration

The email backend is configured to use environment variables from your `.env` file.

## Development Mode (Default)

By default, emails are sent to the console (terminal). This is perfect for development and testing.

**No configuration needed** - it works out of the box!

## Production Mode (SMTP)

To send real emails, configure SMTP settings in your `.env` file:

### Gmail Example

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@devblog.com
```

**Important for Gmail:**
1. Enable 2-Step Verification on your Google account
2. Generate an "App Password" (not your regular password)
3. Use the App Password in `EMAIL_HOST_PASSWORD`

### Outlook/Hotmail Example

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@devblog.com
```

### Yahoo Example

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mail.yahoo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@yahoo.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@devblog.com
```

### Custom SMTP Server

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=your-smtp-server.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-username
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=noreply@devblog.com
```

## Environment Variables

Add these to your `.env` file:

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@devblog.com
```

## Email Types Sent

1. **Account Activation Email** - Sent when user registers
2. **Password Reset Email** - Sent when user requests password reset

## Testing

To test email sending:

1. **Development**: Register a new user - email will appear in console
2. **Production**: Register a new user - email will be sent to the user's email address

## Troubleshooting

### Gmail Issues
- Make sure 2-Step Verification is enabled
- Use App Password, not regular password
- Check that "Less secure app access" is enabled (if using older method)

### Connection Errors
- Check firewall settings
- Verify port numbers (587 for TLS, 465 for SSL)
- Ensure EMAIL_USE_TLS or EMAIL_USE_SSL matches your provider

### Authentication Errors
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
- Check for extra spaces in .env file
- Ensure credentials are not quoted in .env file

