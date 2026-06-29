from textwrap import dedent

from anthropic import AsyncAnthropic

from app.config import settings

MODEL = "claude-haiku-4-5"

_client = AsyncAnthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = dedent("""\
    You are a music journalist writing concise artist bios for a music discovery site.
    Write only from the facts given to you in the user message — never invent biographical
    details, awards, collaborations, or chart positions that aren't in the input.
    Output plain prose, no markdown, no headings, around 150 words.
    """)


async def generate_bio(
    name: str,
    discogs_profile: str | None,
    genres: list[str],
    active_years: str | None,
    genius_bio: str | None = None,
) -> str:
    facts = [f"Artist name: {name}"]
    if genres:
        facts.append(f"Genres: {', '.join(genres)}")
    if active_years:
        facts.append(f"Active years: {active_years}")
    if discogs_profile:
        facts.append(f"Discogs profile notes: {discogs_profile}")
    if genius_bio:
        facts.append(f"Genius bio notes: {genius_bio}")

    response = await _client.messages.create(
        model=MODEL,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": "\n".join(facts)}],
    )
    return next(block.text for block in response.content if block.type == "text")
