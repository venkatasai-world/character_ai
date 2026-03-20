# AI Character App - Walkthrough

## What Was Built

A **production-ready full-stack AI Character Chat App** built with Flask, SQLite, Gemini 2.5 Flash, and Resend API — matching the provided design image.

## Screenshots

### Chat UI (Matches Design Image)
![Chat - Welcome Screen](file:///C:/Users/VENKATA%20SAI/.gemini/antigravity/brain/333f0c4e-2605-4f1c-863c-c7c395fab854/chat_interaction_1774032442598.png)
*Sidebar with character list + user profile + starfield background*

![Chat - Typing Indicator](file:///C:/Users/VENKATA%20SAI/.gemini/antigravity/brain/333f0c4e-2605-4f1c-863c-c7c395fab854/chat_interaction_final_1774032481614.png)
*AI typing indicator animating while Gemini generates response*

## Browser Recording
![Full App Test](file:///C:/Users/VENKATA%20SAI/.gemini/antigravity/brain/333f0c4e-2605-4f1c-863c-c7c395fab854/ai_character_app_test_1774032344803.webp)

## All Pages Built
| Page | Route |
|------|-------|
| 🚀 Landing | `/` |
| 🔐 Login | `/auth/login` |
| ✨ Register | `/auth/register` |
| 🔑 Forgot Password | `/auth/forgot-password` |
| 🔒 Reset Password | `/auth/reset-password/<token>` |
| 📊 Dashboard | `/dashboard` |
| 🎭 Create Character | `/characters/create` |
| ✏️ Edit Character | `/characters/edit/<id>` |
| 💬 Chat | `/chat/<character_id>` |
| 👤 Profile | `/profile/` |

## Features Verified ✅
- **Auth**: Register, login, logout, forgot/reset password  
- **AI Chat**: Gemini 2.5 Flash with personality-aware responses  
- **Typing indicator**: Animated 3-dot bounce while AI responds  
- **Sticker panel**: Grid panel with WhatsApp-style layout  
- **Emoji panel**: 50 emoji quick-insert  
- **Voice input**: Web Speech API (mic button)  
- **Voice output**: Text-to-speech toggle  
- **Language selector**: 13 languages in sidebar  
- **Character CRUD**: Create, edit, delete with avatar upload  
- **Chat export**: Download as [.txt](file:///c:/Users/VENKATA%20SAI/Downloads/ai_character/requirements.txt)  
- **Email**: Resend API for welcome and password reset emails  
- **Dark theme + glassmorphism + neon**: Matches design image  
- **Animated star background**: Throughout the app  
- **Notifications badge**: On bell icon  

## How to Run
```bash
cd ai_character
pip install -r requirements.txt
python app.py
# → http://localhost:5000
```

## Deploy to Render
1. Push repo to GitHub
2. Create new Web Service on Render
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `gunicorn app:app`
5. Add environment variables from [.env](file:///c:/Users/VENKATA%20SAI/Downloads/ai_character/.env)
