"""Configure local admin access without committing or printing credentials."""
import os
import secrets
from getpass import getpass
from pathlib import Path
from dotenv import dotenv_values, set_key
from werkzeug.security import generate_password_hash


def configure(path, email, password):
    email = email.strip().casefold()
    if not email or '@' not in email or not password:
        raise ValueError('Enter a valid email and a non-empty password.')
    path = Path(path)
    path.touch(mode=0o600, exist_ok=True)
    values = dotenv_values(path)
    set_key(path, 'ADMIN_EMAIL', email)
    set_key(path, 'ADMIN_PASSWORD', '')
    set_key(path, 'ADMIN_PASSWORD_HASH', generate_password_hash(password))
    if not values.get('AUTH_SECRET') or values.get('AUTH_SECRET') == 'replace-with-a-long-random-secret':
        set_key(path, 'AUTH_SECRET', secrets.token_hex(32))


def main():
    if os.getenv('VERCEL') or os.getenv('RENDER') or os.getenv('APP_ENV') == 'production':
        raise SystemExit('Configure ADMIN_EMAIL and ADMIN_PASSWORD in your hosting environment settings, then redeploy.')
    email = input('Admin email: ')
    password = getpass('Admin password: ')
    if password != getpass('Confirm password: '):
        raise SystemExit('Passwords do not match. No changes saved.')
    configure(Path(__file__).resolve().parent / '.env', email, password)
    print('Admin configuration saved locally. Restart the app. Do not commit .env.')


if __name__ == '__main__':
    main()
