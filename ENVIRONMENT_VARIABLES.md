# Environment Variables

This application requires the following environment variables to be set:

## Required Variables

### Supabase Configuration
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY` - Your Supabase anon/public key

### Make.com Webhooks
- `VITE_MAKE_WEBHOOK_URL` - Webhook URL for student questionnaire submissions
- `VITE_MAKE_TUTOR_WEBHOOK_URL` - Webhook URL for tutor application submissions

### Google Analytics (Optional)
- `VITE_GA_MEASUREMENT_ID` - Google Analytics 4 (GA4) Measurement ID (e.g., G-XXXXXXXXXX)

## CV Upload Setup

The tutor application now sends CV files as base64 data through the webhook instead of uploading to Supabase storage. This avoids RLS policy issues with anonymous users.

The webhook will receive:
- `cvFileName`: Original filename
- `cvFileData`: Base64 encoded file content
- `cvFileType`: MIME type of the file

## Example .env file

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
VITE_MAKE_WEBHOOK_URL=https://hook.eu1.make.com/your-student-webhook
VITE_MAKE_TUTOR_WEBHOOK_URL=https://hook.eu1.make.com/your-tutor-webhook
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX
```

## Webhook Payloads

### Student Questionnaire Webhook
```json
{
  "course": "string",
  "helpTypes": ["string"],
  "whenNeeded": "string", 
  "name": "string",
  "email": "string",
  "timestamp": "ISO string",
  "source": "carre-das-questionnaire"
}
```

### Tutor Application Webhook
```json
{
  "prenom": "string",
  "nom": "string", 
  "email": "string",
  "telephone": "string",
  "domaineEtude": ["string"],
  "autreDomaine": "string (optional)",
  "niveauEtude": "string",
  "disponibilites": ["string"],
  "experienceTutorat": "string",
  "cvFileName": "string (optional)",
  "cvFileData": "string (base64, optional)",
  "cvFileType": "string (optional)",
  "timestamp": "ISO string",
  "source": "carre-das-tutor-application"
}
```
