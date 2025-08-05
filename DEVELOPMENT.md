# Xeyronox Link Bot - Complete Deployment Guide

## ðŸŽ¯ Quick Start Checklist

- [ ] Create Telegram bot with @BotFather
- [ ] Fork/clone this repository to GitHub
- [ ] Create Render.com account
- [ ] Deploy as Web Service on Render
- [ ] Set environment variables
- [ ] Test the bot

## ðŸ“‹ Detailed Deployment Steps

### Step 1: Create Telegram Bot

1. **Open Telegram** and search for `@BotFather`
2. **Start conversation** by sending `/start`
3. **Create new bot** by sending `/newbot`
4. **Choose bot name**: `Xeyronox Link Bot` (or your preferred name)
5. **Choose username**: `XeyronoxLinkBot` (must end with 'bot')
6. **Save the token**: Copy the token provided (keep it secure!)

### Step 2: Prepare GitHub Repository

1. **Fork this repository** or create a new one
2. **Upload all files**:
   - `app.py` (main bot code)
   - `requirements.txt` (dependencies)
   - `README.md` (documentation)
   - `.env.example` (template)

### Step 3: Deploy on Render.com

#### 3.1 Create Account
- Go to [render.com](https://render.com)
- Sign up with GitHub (recommended)

#### 3.2 Create Web Service
1. Click **"New"** â†’ **"Web Service"**
2. **Connect GitHub repository**
3. **Select your bot repository**

#### 3.3 Configure Service Settings
```
Service Name: xeyronox-link-bot
Region: [Choose closest to your users]
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

#### 3.4 Set Environment Variables
In the **Environment** section, add:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
WEBHOOK_URL=https://xeyronox-link-bot.onrender.com
```

**âš ï¸ Replace with your actual bot token!**

#### 3.5 Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for deployment
- Check logs for "Webhook set to..." confirmation

### Step 4: Verify Deployment

#### 4.1 Test Health Endpoint
```bash
curl https://xeyronox-link-bot.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "bot": "Xeyronox Link Bot", 
  "version": "1.0.0"
}
```

#### 4.2 Test Bot Commands
1. Search for your bot in Telegram: `@XeyronoxLinkBot`
2. Send `/start` command
3. Verify inline buttons appear
4. Test other commands: `/help`, `/links`, `/shop`

## ðŸ”§ Environment Variables Explained

### Required Variables

**TELEGRAM_BOT_TOKEN**
- **Description**: Your bot's authentication token
- **Example**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
- **Source**: @BotFather in Telegram

**WEBHOOK_URL** 
- **Description**: Your Render app's public URL
- **Example**: `https://xeyronox-link-bot.onrender.com`
- **Note**: Replace 'xeyronox-link-bot' with your actual service name

### Optional Variables

**PORT**
- **Description**: Port for the web server
- **Default**: `10000` (Render's default)
- **Note**: Usually handled automatically by Render

## ðŸš€ Advanced Configuration

### Custom Domain (Optional)
1. Go to **Settings** â†’ **Custom Domains**
2. Add your domain
3. Update `WEBHOOK_URL` environment variable
4. Redeploy the service

### Auto-Deploy Setup
1. Go to **Settings** â†’ **Auto-Deploy**
2. Choose **"Auto-deploy from GitHub"**
3. Select branch (usually `main`)
4. Save settings

### Monitoring Setup
1. **Built-in Monitoring**: Available in Render dashboard
2. **External Monitoring**: Use health endpoint
   ```
   URL: https://your-app.onrender.com/health
   Method: GET
   Expected: HTTP 200
   ```

## ðŸ›  Troubleshooting

### Common Issues & Solutions

#### Issue: "Bot not responding"
**Symptoms**: Bot doesn't reply to messages

**Solutions**:
1. Check webhook status:
   ```bash
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```
2. Verify environment variables in Render
3. Check deployment logs for errors
4. Ensure service is running (not sleeping)

#### Issue: "Deployment failed"
**Symptoms**: Build fails or service won't start

**Solutions**:
1. Check `requirements.txt` syntax
2. Verify all files are in repository
3. Check Python version compatibility
4. Review build logs in Render dashboard

#### Issue: "Health check failing"
**Symptoms**: `/health` endpoint returns errors

**Solutions**:
1. Verify Flask app is running
2. Check if port binding is correct
3. Ensure no Python syntax errors
4. Review application logs

#### Issue: "Webhook not set"
**Symptoms**: Bot receives no updates

**Solutions**:
1. Check `WEBHOOK_URL` environment variable
2. Ensure URL is accessible publicly
3. Verify bot token is correct
4. Restart the service

### Debug Commands

```bash
# Check webhook info
curl "https://api.telegram.org/bot<YOUR_TOKEN>/getWebhookInfo"

# Test health endpoint  
curl "https://your-app-name.onrender.com/health"

# Test root endpoint
curl "https://your-app-name.onrender.com/"

# Delete webhook (if needed)
curl "https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook"
```

## ðŸ“Š Monitoring & Maintenance

### Health Monitoring
Set up monitoring for:
- **Health endpoint**: `/health`
- **Response time**: Should be < 5 seconds
- **Uptime**: Target 99%+ availability

### Log Monitoring
Watch for:
- Webhook processing errors
- Bot initialization failures
- Rate limiting issues
- Memory/CPU usage spikes

### Regular Maintenance
- **Weekly**: Check logs for errors
- **Monthly**: Review bot usage analytics
- **Quarterly**: Update dependencies
- **As needed**: Add new features

## ðŸ” Security Best Practices

### Token Security
- âœ… Store token in environment variables
- âœ… Never commit tokens to Git
- âœ… Use Render's secure variable storage
- âŒ Don't expose tokens in logs

### Access Control
- âœ… Use HTTPS for all communications
- âœ… Validate all incoming data
- âœ… Implement rate limiting if needed
- âœ… Monitor for unusual activity

### Infrastructure Security
- âœ… Keep dependencies updated
- âœ… Use official Docker images
- âœ… Enable security headers
- âœ… Regular security audits

## ðŸ“ˆ Scaling Considerations

### Traffic Growth
- Monitor response times
- Consider upgrading Render plan
- Implement caching if needed
- Use CDN for static assets

### Feature Expansion
- Add database for user data
- Implement user analytics
- Add multi-language support
- Create admin dashboard

## ðŸ†˜ Getting Help

### Documentation
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [python-telegram-bot Docs](https://docs.python-telegram-bot.org/)
- [Render Documentation](https://render.com/docs)

### Support Channels
- **GitHub Issues**: For code-related problems
- **Render Support**: For deployment issues
- **Telegram**: @Xeyronox for direct support

---

ðŸ”¥ **Deploy with confidence!** ðŸ”¥

**Developer**: Xeyronox || Red/Black Hat Hacker