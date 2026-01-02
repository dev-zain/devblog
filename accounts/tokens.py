from django.contrib.auth.tokens import PasswordResetTokenGenerator


class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        # Safely get email_verified, default to False if profile doesn't exist
        email_verified = getattr(user.profile, 'email_verified', False) if hasattr(user, 'profile') else False
        
        return (
            str(user.pk) +
            str(timestamp) +
            str(email_verified)
        )


account_activation_token = AccountActivationTokenGenerator()