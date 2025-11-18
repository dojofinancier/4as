# API Comparison: Models with Internet Access

## Summary
For generating external links with real-time internet access, **Perplexity AI** is the most cost-effective and suitable option.

## Option 1: Perplexity AI ⭐ RECOMMENDED

### Features
- ✅ Real-time internet access and web search
- ✅ Can find actual, accessible URLs
- ✅ API available for integration
- ✅ Citations and source verification

### Pricing

#### Subscription Plans
- **Free Plan**: $0/month
  - Limited API access
  - 3-5 Pro searches per day
  
- **Pro Plan**: $20/month or $200/year ⭐ BEST VALUE
  - Unlimited Pro searches
  - $5 monthly API credit included
  - Access to advanced models (GPT-4.1, Claude 3.7 Sonnet)
  
- **Max Plan**: $200/month
  - All Pro features
  - Early access to new features

#### API Pricing (Pay-as-you-go)
- **Sonar Model**: 
  - Input: $1 per million tokens
  - Output: $1 per million tokens
  - **Estimated cost per article**: ~$0.001-0.002 (assuming 1K input + 1K output tokens)

- **Sonar Pro Model**:
  - Input: $3 per million tokens
  - Output: $15 per million tokens
  - **Estimated cost per article**: ~$0.003-0.018

- **Sonar Deep Research**:
  - Input: $2 per million tokens
  - Output: $8 per million tokens
  - Search queries: $5 per 1,000 queries
  - **Best for**: Finding specific URLs with citations

### Cost Estimate for 100 Articles
- Using **Sonar** (basic): ~$0.10 - $0.20 total
- Using **Sonar Pro**: ~$0.30 - $1.80 total
- With Pro subscription ($20/month): Includes $5 credit = **FREE for 100 articles** (or even 500+ articles)

### Integration
- Python SDK available
- REST API
- Can search web and return real URLs with citations

---

## Option 2: ChatGPT Atlas

### Features
- ✅ Real-time internet access
- ❌ Primarily a browser, not an API service
- ❌ Limited API access (requires Enterprise plan)

### Pricing
- **Free**: $0/month (limited features)
- **Plus**: $20/month (browser only, no API)
- **Pro**: $200/month (browser only, no API)
- **Enterprise**: Custom pricing (includes API access)

### Verdict
❌ **Not suitable** - No public API for programmatic use

---

## Option 3: You.com / YouChat

### Features
- ✅ Real-time web search
- ❌ Limited API availability
- ❌ Pricing not clearly documented for API

### Verdict
❌ **Not suitable** - API access unclear/limited

---

## Option 4: Grok (xAI)

### Features
- ✅ Real-time internet access
- ❌ API pricing not clearly documented
- ❌ Less mature ecosystem

### Verdict
❌ **Not suitable** - Limited API documentation

---

## Recommendation: Perplexity AI

### Why Perplexity?
1. **Cost-effective**: $20/month Pro plan includes $5 API credit (enough for 500+ articles)
2. **Real internet access**: Can find actual, accessible URLs
3. **Well-documented API**: Python SDK available
4. **Citations**: Returns source URLs with citations
5. **Reliable**: Established service with good documentation

### Implementation Strategy
1. Use **Sonar** model for basic URL finding (cheapest)
2. Use **Sonar Deep Research** if we need more thorough search
3. Subscribe to **Pro plan** ($20/month) to get $5 monthly credit
4. For 100 articles, the $5 credit should cover everything

### Next Steps
1. Sign up for Perplexity Pro ($20/month) at https://www.perplexity.ai/
2. Get API key from Perplexity dashboard (Settings > API Keys)
3. Add `PERPLEXITY_API_KEY` to `.env` file
4. Install Perplexity Python SDK (if available) or use HTTP requests
5. Modify `add_external_links.py` to use Perplexity API instead of GPT-5-nano

### API Usage
Perplexity API uses OpenAI-compatible format:
- Base URL: `https://api.perplexity.ai`
- Endpoint: `/chat/completions`
- Models: `sonar`, `sonar-pro`, `sonar-reasoning`, `sonar-deep-research`
- Headers: `Authorization: Bearer {PERPLEXITY_API_KEY}`

### Cost Estimate for 100 Articles
- **Sonar model**: ~$0.10 - $0.20 total (1K input + 1K output tokens per article)
- **With Pro subscription**: $5 monthly credit covers 500+ articles = **FREE**
- **Without subscription**: Pay-as-you-go, still very affordable

### Implementation Notes
- Perplexity API returns citations with URLs automatically
- Can extract real URLs from citations
- Still validate URLs with `requests` library as backup
- Perplexity will find actual, accessible URLs from the web

