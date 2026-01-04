// Vercel Serverless Function for Story Generation
// Uses Anthropic Claude API

export default async function handler(req, res) {
  // Only allow POST
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  // Check for API key
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return res.status(500).json({ error: 'API key not configured' });
  }

  try {
    const { prompt } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'Prompt is required' });
    }

    // Call Claude API
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 4096,
        messages: [
          {
            role: 'user',
            content: prompt
          }
        ]
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Claude API error:', errorData);
      return res.status(response.status).json({ error: 'Failed to generate story' });
    }

    const data = await response.json();

    // Extract the JSON from Claude's response
    const content = data.content[0].text;

    // Try to parse the JSON response
    let storyData;
    try {
      // Find JSON in the response (handle if Claude adds extra text)
      const jsonMatch = content.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        storyData = JSON.parse(jsonMatch[0]);
      } else {
        throw new Error('No JSON found in response');
      }
    } catch (parseError) {
      console.error('Failed to parse story JSON:', parseError);
      return res.status(500).json({
        error: 'Failed to parse story',
        raw: content
      });
    }

    return res.status(200).json(storyData);

  } catch (error) {
    console.error('Error generating story:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
