# FROM (old parsing):
        try:
            clean = re.sub(r"```json\n?|```\n?", "", raw).strip()
            start = clean.find("{")
            end = clean.rfind("}") + 1
            if start != -1 and end > start:
                clean = clean[start:end]
            data = json.loads(clean)
        except Exception:
            data = {
                "posts_analyzed": len(all_posts),
                "personas": [], "common_pain_points": [],
                "jobs_to_be_done": [], "buying_triggers": [],
                "raw_quotes": [], "error": "parse_failed",
            }

        # TO (new parsing):
        try:
            data = json.loads(self.extract_json(raw))
        except Exception as e:
            data = {
                "posts_analyzed": len(all_posts),
                "personas": [], "common_pain_points": [],
                "jobs_to_be_done": [], "buying_triggers": [],
                "raw_quotes": [], "parse_error": str(e), "raw_response": raw[:500],
            }
