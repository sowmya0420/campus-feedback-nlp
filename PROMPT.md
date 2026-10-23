# Synthetic campus feedback: generation prompt

Fill in {FACILITY}, {ASPECTS}, {PERSONAS}, then paste into a fresh chat (one chat per facility batch).
Save the JSON output as data/raw/<file_name>.json  (second batch: <file_name>_2.json).

## Facilities (file name -> FACILITY -> ASPECTS = allowed categories)

| file_name    | FACILITY                         | ASPECTS (categories) |
|--------------|----------------------------------|----------------------|
| hostel_mess  | hostel mess                      | food quality, price, hygiene, waiting time, seating, staff behavior, quantity, variety |
| canteen      | campus canteen / food court      | food quality, price, hygiene, waiting time, seating, staff behavior, quantity, variety |
| library      | library                          | book availability, seating, silence, opening hours, staff behavior, cleanliness, ac/temperature, digital resources |
| hostel_rooms | hostel rooms and facilities      | cleanliness, water supply, electricity, maintenance, room size, safety, laundry, noise |
| labs         | computer and engineering labs    | equipment condition, system speed, software availability, lab staff, lab timings, cleanliness, space |
| wifi         | campus Wi-Fi / internet          | speed, connectivity, coverage, login issues, reliability, bandwidth limit |
| transport    | college bus transport            | punctuality, crowding, driver behavior, route coverage, bus condition, safety, fare |
| classrooms   | classrooms (optional)            | ac/temperature, seating, projector/av, cleanliness, lighting, noise |

Personas batch 1: first-year hosteller, second-year day scholar, final-year student, girls' hostel resident, outstation student
Personas batch 2: placement-focused student, club member, backlog student, third-year hosteller, faculty-project student

## Prompt

```
ROLE: You are generating a labeled dataset of student feedback for an NLP
research project (aspect-based sentiment analysis) at an Indian engineering
college in Tamil Nadu.

TASK: Generate exactly 50 distinct student comments about: {FACILITY}.

ALLOWED CATEGORY LABELS (use only these, lowercase):
{ASPECTS}

ALLOWED SENTIMENTS: positive, negative, neutral

DISTRIBUTION (approximate):
- Overall: 40% negative, 35% positive, 25% mixed (one aspect praised, another criticised)
- Length: 40% short (3-8 words), 40% medium (1-2 sentences), 20% long (3-4 sentences)
- 30% of comments mention 2-3 different aspects
- Style: formal, casual slang, a few typos, ~15% Tanglish (Tamil + English written
  in Roman letters, e.g. "food semma but queue romba long")
- Exactly 3 comments must be abusive/toxic (insults or profanity) -> "abusive": true
- Write from these perspectives, spread evenly: {PERSONAS}

RULES:
- Sound like real students typing quickly. No marketing language.
- No repeated sentence openings or templates.
- No real people's names or registration numbers.
- For each aspect, "aspect_term" must be the EXACT word(s) copied from the comment
  text (same spelling). Use null if the aspect is implied but not stated.
- "category" must be one of the allowed category labels.
- If a comment is only an insult with no facility opinion, use "aspects": [].

EXAMPLE FORMAT (do not copy these):
[
 {"text": "food is tasty but the queue takes forever", "aspects": [
   {"aspect_term": "food", "category": "food quality", "sentiment": "positive"},
   {"aspect_term": "queue", "category": "waiting time", "sentiment": "negative"}],
  "abusive": false},
 {"text": "mess food is trash, whoever cooks this is an idiot", "aspects": [
   {"aspect_term": "food", "category": "food quality", "sentiment": "negative"}],
  "abusive": true}
]

OUTPUT: Return ONLY the JSON array of 50 objects. No explanation, no markdown fences.
```
