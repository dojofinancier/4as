# Environment Variables

This application requires the following environment variables to be set:

## Required Variables

### Supabase Configuration
- `VITE_SUPABASE_URL` - Your Supabase project URL
- `VITE_SUPABASE_PUBLISHABLE_KEY` - Your Supabase anon/public key

### Make.com Webhooks
- `VITE_MAKE_WEBHOOK_URL` - Webhook URL for student questionnaire submissions
- `VITE_MAKE_TUTOR_WEBHOOK_URL` - Webhook URL for tutor application submissions

## Supabase Storage Setup

For the tutor application CV uploads to work, you need to:

1. Create a storage bucket named `recruitment` in your Supabase project
2. Set the bucket to public or configure appropriate RLS policies
3. Ensure the bucket allows file uploads with the following extensions: `.pdf`, `.doc`, `.docx`

## Example .env file

```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_PUBLISHABLE_KEY=your-anon-key
VITE_MAKE_WEBHOOK_URL=https://hook.eu1.make.com/your-student-webhook
VITE_MAKE_TUTOR_WEBHOOK_URL=https://hook.eu1.make.com/your-tutor-webhook
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
  "cvUrl": "string",
  "timestamp": "ISO string",
  "source": "carre-das-tutor-application"
}
```
