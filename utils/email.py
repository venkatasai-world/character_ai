"""
Email Helper - Resend API Integration
"""
import os
import resend
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv('RESEND_API_KEY')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'onboarding@resend.dev')
APP_URL = os.getenv('APP_URL', 'http://localhost:5000')


def send_welcome_email(user_name: str, user_email: str) -> bool:
    """Send welcome email after registration"""
    try:
        params = {
            "from": f"AI Character App <{FROM_EMAIL}>",
            "to": [user_email],
            "subject": f"Welcome to AI Character App, {user_name}! 🤖✨",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a1a; color: #e0e0ff; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: linear-gradient(135deg, #1a1a3e 0%, #0d0d2b 100%); border-radius: 20px; overflow: hidden; border: 1px solid rgba(124, 58, 237, 0.3); }}
        .header {{ background: linear-gradient(135deg, #7c3aed, #ec4899); padding: 50px 40px; text-align: center; }}
        .header h1 {{ color: white; font-size: 32px; margin: 0; font-weight: 800; }}
        .header .emoji {{ font-size: 60px; margin-bottom: 15px; display: block; }}
        .body {{ padding: 40px; }}
        .body h2 {{ color: #a78bfa; font-size: 24px; margin-top: 0; }}
        .features {{ display: flex; flex-wrap: wrap; gap: 15px; margin: 25px 0; }}
        .feature {{ background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 12px; padding: 15px; flex: 1; min-width: 120px; text-align: center; }}
        .feature .icon {{ font-size: 28px; margin-bottom: 8px; }}
        .feature p {{ margin: 0; font-size: 12px; color: #c4b5fd; }}
        .cta {{ text-align: center; margin: 30px 0; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #ec4899); color: white; padding: 16px 40px; border-radius: 50px; text-decoration: none; font-weight: 700; font-size: 16px; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.05); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="emoji">🤖</span>
            <h1>Welcome to AI Character!</h1>
        </div>
        <div class="body">
            <h2>Hi {user_name}! 👋</h2>
            <p>You've successfully joined the future of AI interaction! Get ready to create and chat with your very own AI characters.</p>
            <div class="features">
                <div class="feature">
                    <div class="icon">🎭</div>
                    <p>Custom AI Characters</p>
                </div>
                <div class="feature">
                    <div class="icon">🎙️</div>
                    <p>Voice Chat</p>
                </div>
                <div class="feature">
                    <div class="icon">🌍</div>
                    <p>Translation</p>
                </div>
                <div class="feature">
                    <div class="icon">😊</div>
                    <p>Sticker Fun</p>
                </div>
            </div>
            <p>Start by creating your first AI character — give it a unique personality, background story, and speaking style!</p>
            <div class="cta">
                <a href="{APP_URL}/dashboard" class="btn">🚀 Get Started Now</a>
            </div>
        </div>
        <div class="footer">
            <p>© 2024 AI Character App · Powered by AI Technology</p>
        </div>
    </div>
</body>
</html>
"""
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Welcome email error: {e}")
        return False


def send_password_reset_email(user_name: str, user_email: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_url = f"{APP_URL}/auth/reset-password/{reset_token}"
    
    try:
        params = {
            "from": f"AI Character App <{FROM_EMAIL}>",
            "to": [user_email],
            "subject": "Reset Your Password - AI Character App 🔐",
            "html": f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; background: #0a0a1a; color: #e0e0ff; margin: 0; padding: 0; }}
        .container {{ max-width: 600px; margin: 40px auto; background: linear-gradient(135deg, #1a1a3e 0%, #0d0d2b 100%); border-radius: 20px; overflow: hidden; border: 1px solid rgba(124, 58, 237, 0.3); }}
        .header {{ background: linear-gradient(135deg, #7c3aed, #ec4899); padding: 40px; text-align: center; }}
        .header h1 {{ color: white; font-size: 28px; margin: 0; }}
        .body {{ padding: 40px; }}
        .body h2 {{ color: #a78bfa; }}
        .warning {{ background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 15px; margin: 20px 0; color: #fca5a5; font-size: 13px; }}
        .cta {{ text-align: center; margin: 30px 0; }}
        .btn {{ display: inline-block; background: linear-gradient(135deg, #7c3aed, #ec4899); color: white; padding: 16px 40px; border-radius: 50px; text-decoration: none; font-weight: 700; }}
        .token-box {{ background: rgba(124, 58, 237, 0.1); border: 1px solid rgba(124, 58, 237, 0.3); border-radius: 10px; padding: 15px; text-align: center; word-break: break-all; font-family: monospace; color: #c4b5fd; margin: 15px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 13px; border-top: 1px solid rgba(255,255,255,0.05); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Password Reset Request</h1>
        </div>
        <div class="body">
            <h2>Hi {user_name},</h2>
            <p>We received a request to reset your password. Click the button below to set a new password:</p>
            <div class="cta">
                <a href="{reset_url}" class="btn">Reset My Password</a>
            </div>
            <p>Or copy this link:</p>
            <div class="token-box">{reset_url}</div>
            <div class="warning">
                ⚠️ This link expires in <strong>1 hour</strong>. If you didn't request this, please ignore this email.
            </div>
        </div>
        <div class="footer">
            <p>© 2024 AI Character App</p>
        </div>
    </div>
</body>
</html>
"""
        }
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Password reset email error: {e}")
        return False
