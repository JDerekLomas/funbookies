# MuleRun Midjourney API Access Issue

## Summary
Attempting to access Midjourney via MuleRun API returns authentication errors, while the same API key works correctly for MuleRouter.

## Environment
- Date: January 1, 2026
- API Key: `sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436`

## What Works ✅

**MuleRouter (api.mulerouter.ai) - Wan2.6 generation:**
```bash
curl -X POST https://api.mulerouter.ai/vendors/alibaba/v1/wan2.6-t2i/generation \
  -H "Authorization: Bearer sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute lime-green gecko"}'
```
**Result:** Success - returns task_id, completes with 4 images

## What Fails ❌

### Attempt 1: MuleRun Midjourney with Bearer auth
```bash
curl -X POST https://api.mulerun.com/vendors/midjourney/v1/tob/diffusion \
  -H "Authorization: Bearer sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute gecko", "mode": "fast"}'
```
**Error:**
```json
{
  "status": 401,
  "title": "Invalid API Key format",
  "detail": "None (request_id: c3532430-97b8-4d1e-ad6c-b9a171538805)",
  "instance": "/vendors/midjourney/v1/tob/diffusion",
  "error_code": 0
}
```

### Attempt 2: MuleRun with x-api-key header
```bash
curl -X POST https://api.mulerun.com/vendors/midjourney/v1/tob/diffusion \
  -H "x-api-key: sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute gecko", "mode": "fast"}'
```
**Error:**
```json
{
  "status": 401,
  "title": "Missing Authorization header. Please provide 'Authorization: Bearer <api_key>'",
  "detail": "None (request_id: 87ba2cd7-7997-459d-80c3-84bda2984b60)",
  "instance": "/vendors/midjourney/v1/tob/diffusion",
  "error_code": 0
}
```

### Attempt 3: MuleRun Wan2.6 (non-Midjourney)
```bash
curl -X POST https://api.mulerun.com/vendors/alibaba/v1/wan2.6-t2i/generation \
  -H "Authorization: Bearer sk-mr-2dfbbdfe5bbd2e24235960b2d4f5b45bf1b59a087bc2524ff35c6c70a2657436" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A cute gecko"}'
```
**Error:**
```json
{
  "status": 404,
  "title": "Not Found"
}
```

### Attempt 4: Using mulerouter-skills Python package
```bash
export MULEROUTER_SITE="mulerun"
export MULEROUTER_API_KEY="sk-mr-..."
uv run python models/midjourney/diffusion/generation.py \
  --prompt "A cute gecko" --mode fast
```
**Error:**
```
Status: failed
Error: None (request_id: 0a23699d-e289-4f75-8297-8e556845a8f5)
```

## Questions for Dev

1. Is the `sk-mr-` API key format valid for MuleRun, or does MuleRun require a different key format?

2. Are MuleRouter and MuleRun separate accounts/subscriptions? The pricing page shows Midjourney is available on MuleRun but our key only works on MuleRouter.

3. What is the correct endpoint path for Midjourney on MuleRun? We tried:
   - `/vendors/midjourney/v1/tob/diffusion` (from docs)

4. Is there a way to check if an API key has Midjourney access enabled?

## Goal
We want to use Midjourney's `--cref` (character reference) parameter for consistent character generation:
```
prompt: "A gecko on a hill --cref https://example.com/gecko.png --cw 100"
```

## References
- MuleRun API docs: https://mulerun.com/docs/api-reference/introduction
- MuleRun pricing (shows Midjourney): https://mulerun.com/docs/creator-guide/pricing/image
