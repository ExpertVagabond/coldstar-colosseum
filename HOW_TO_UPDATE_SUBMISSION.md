# How to Update Your Colosseum Submission

Since the API key isn't stored locally, use this browser console method to update your project.

## Method 1: Browser Console Script (Recommended)

### Step 1: Open Colosseum
Go to https://colosseum.com/agent-hackathon and log in as **coldstar-agent**

### Step 2: Open Browser Console
- **Chrome/Edge**: Press F12 or Ctrl+Shift+J (Cmd+Option+J on Mac)
- **Firefox**: Press F12 or Ctrl+Shift+K (Cmd+Option+K on Mac)
- **Safari**: Enable Developer menu first, then Cmd+Option+C

### Step 3: Copy and Paste Script
1. Open the file: `update-colosseum-project.js`
2. Copy the entire contents
3. Paste into the browser console
4. Press Enter

### Step 4: Follow Prompts
- The script will try to find your API key automatically
- If it can't find it, you'll be prompted to enter it
- It will update your project with the demo link
- You'll be asked if you want to submit for judging

## Method 2: Manual Web Update

### Step 1: Login
Go to https://colosseum.com/agent-hackathon

### Step 2: Navigate to Your Project
Click on "My Project" or go directly to:
https://colosseum.com/agent-hackathon/projects/coldstar-air-gapped-solana-vault-2z9v3x

### Step 3: Edit Project
Look for an "Edit" button and update:

**Technical Demo Link:**
```
https://coldstar.dev/colosseum
```

**Presentation Link:** (add when video is ready)
```
[Your YouTube URL]
```

### Step 4: Submit
When everything looks good, click "Submit for Judging"

⚠️ **WARNING**: After submission, the project is LOCKED and cannot be edited!

---

## Method 3: API Key Recovery

If you can find your API key (starts with `ahk_`), check these locations:

1. **Email**: Search your inbox for "Colosseum" or "hackathon"
2. **Browser Downloads**: Check downloads from Feb 2, 2026
3. **Password Manager**: If you use 1Password, LastPass, etc.
4. **Browser LocalStorage**:
   - Open browser console (F12)
   - Go to Application → Local Storage → https://colosseum.com
   - Look for `apiKey` or similar

Once you find it, you can update via API:

```bash
curl -X PUT https://agents.colosseum.com/api/my-project \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "technicalDemoLink": "https://coldstar.dev/colosseum"
  }'
```

Then submit:

```bash
curl -X POST https://agents.colosseum.com/api/my-project/submit \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## What Gets Updated

✅ Demo URL: https://coldstar.dev/colosseum
✅ Current description (already good)
✅ Current Solana integration description (already detailed)
⏳ Video link (add when ready)

## Current Project Status

- **Name**: Coldstar - Air-Gapped Solana Vault
- **Owner**: coldstar-final (ID: 127)
- **Status**: DRAFT (needs to be submitted)
- **Upvotes**: 2 human upvotes already!
- **Team**: coldstar-agent's Team

## Timeline

- **Deadline**: February 12, 2026 at 12:00 PM EST
- **Days Remaining**: 9 days
- **Next Steps**:
  1. Update project with demo link
  2. Record video (guide in VIDEO_RECORDING_GUIDE.md)
  3. Add video link
  4. Submit for judging

---

## Need Help?

If none of these methods work, contact Colosseum support:
- Forum: https://colosseum.com/agent-hackathon/forum
- Create a support post with tag "technical-help"

Your project exists and has upvotes - you just need to add the demo link and submit!
