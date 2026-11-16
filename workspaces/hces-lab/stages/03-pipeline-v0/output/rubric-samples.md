# Stage 03 Rubric Samples

Checkpoint after step 2. Every rubric has the same four parts; only the wording changes per question. All 25 Secret Adversary rubrics are in `rubrics-secret-adversary.jsonl`, versioned and hashed.

Code turns the relevance level into a 0 to 1 score (level / 4). A passage where `contains_fact` is likely yes is always kept, whatever its score. The rubric never contains the answer, so needles are not given away.

## q01: plain question, one gold passage

**Question:** Where did Jane Finn hide the oilskin packet after the shipwreck?

| Part | Type | Wording |
|------|------|---------|
| Relevance | Score, 5 levels | How directly does this passage help answer: Where did Jane Finn hide the oilskin packet after the shipwreck? |
| Level 0 | anchor | Unrelated to the question. |
| Level 1 | anchor | Shares words or names with the question but says nothing about Jane Finn and the oilskin packet after the Lusitania sank. |
| Level 2 | anchor | About Jane Finn and the oilskin packet after the Lusitania sank, but does not touch the place where Jane Finn hid the oilskin packet. |
| Level 3 | anchor | Gives part of the place where Jane Finn hid the oilskin packet, or strong clues to it. |
| Level 4 | anchor | States the place where Jane Finn hid the oilskin packet plainly. |
| Contains fact (critical) | Noul | Does this passage itself state the place where Jane Finn hid the oilskin packet? |
| Evidence form | Choice | How does this passage present anything about the question? Options: dialogue (A character says it.); document (A letter, note, card or printed text shows it.); narration (The narrator states it.); none (Nothing about the question appears.) |
| Answerability | Noul, once per kept set | Taken together, do these passages give enough to answer: Where did Jane Finn hide the oilskin packet after the shipwreck? |

Hash `cca9b9568dc5`

## q10: low overlap: the answer shares few words with the question

**Question:** How did the two friends first plan to earn money after the war?

| Part | Type | Wording |
|------|------|---------|
| Relevance | Score, 5 levels | How directly does this passage help answer: How did the two friends first plan to earn money after the war? |
| Level 0 | anchor | Unrelated to the question. |
| Level 1 | anchor | Shares words or names with the question but says nothing about Tommy and Tuppence's money troubles after the war. |
| Level 2 | anchor | About Tommy and Tuppence's money troubles after the war, but does not touch the plan Tommy and Tuppence first made to earn money. |
| Level 3 | anchor | Gives part of the plan Tommy and Tuppence first made to earn money, or strong clues to it. |
| Level 4 | anchor | States the plan Tommy and Tuppence first made to earn money plainly. |
| Contains fact (critical) | Noul | Does this passage itself state the plan Tommy and Tuppence first made to earn money? |
| Evidence form | Choice | How does this passage present anything about the question? Options: dialogue (A character says it.); document (A letter, note, card or printed text shows it.); narration (The narrator states it.); none (Nothing about the question appears.) |
| Answerability | Noul, once per kept set | Taken together, do these passages give enough to answer: How did the two friends first plan to earn money after the war? |

Hash `c2ead5329aec`

## n03: needle with a lookalike decoy

**Question:** What number was engraved on Julius's gold cigarette case?

| Part | Type | Wording |
|------|------|---------|
| Relevance | Score, 5 levels | How directly does this passage help answer: What number was engraved on Julius's gold cigarette case? |
| Level 0 | anchor | Unrelated to the question. |
| Level 1 | anchor | Shares words or names with the question but says nothing about Julius's belongings or his father's fortune. |
| Level 2 | anchor | About Julius's belongings or his father's fortune, but does not touch a number engraved on Julius Hersheimmer's cigarette case. |
| Level 3 | anchor | Gives part of a number engraved on Julius Hersheimmer's cigarette case, or strong clues to it. |
| Level 4 | anchor | States a number engraved on Julius Hersheimmer's cigarette case plainly. |
| Contains fact (critical) | Noul | Does this passage itself state a number engraved on Julius Hersheimmer's cigarette case? |
| Evidence form | Choice | How does this passage present anything about the question? Options: dialogue (A character says it.); document (A letter, note, card or printed text shows it.); narration (The narrator states it.); none (Nothing about the question appears.) |
| Answerability | Noul, once per kept set | Taken together, do these passages give enough to answer: What number was engraved on Julius's gold cigarette case? |

Hash `7dc24363e838`

