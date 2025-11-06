import json
import re
import requests
from typing import Dict

from app.core.vector_client import VectorDB
from app.core.redis_cient import get_memory, save_memory
from app.services.embedding import create_ollama_embedding
from app.core.database import Booking, SessionLocal
from app.core.config import GEMINI_API_KEY


def _parse_booking_fallback(query: str) -> Dict[str, str]:
	"""Original regex-based fallback parser.

	Keeps behaviour compatible with previous implementation in case LLM fails.
	"""
	name = re.search(r"name\s+is\s+(\w+)", query, re.IGNORECASE)
	email = re.search(r"[\w\.-]+@[\w\.-]+", query)
	date = re.search(r"(\d{4}-\d{2}-\d{2})", query)
	time = re.search(r"(\d{1,2}:\d{2})", query)
	return {
		"name": name.group(1) if name else "Unknown",
		"email": email.group(0) if email else "Unknown",
		"date": date.group(1) if date else "TBD",
		"time": time.group(1) if time else "TBD",
	}

def parse_booking(query: str) -> Dict[str, str]:
	"""Extract booking fields (name, email, date, time) using Gemini LLM.

	The function will call the configured Gemini endpoint and instruct it to
	return a JSON object with the keys: name, email, date, time. Date should be
	in YYYY-MM-DD when possible and time in HH:MM (24h or 12h) when possible.

	If the LLM call fails or does not return parseable JSON, the function
	falls back to a conservative regex extractor.
	"""
	prompt = (
		"Extract the following fields from the user text and respond ONLY with a "
		"JSON object (no additional text). Fields: name, email, date, time. "
		"Use ISO date format YYYY-MM-DD if possible. Use HH:MM for time. "
		"If a field is missing, set name/email to \"Unknown\" and date/time to \"TBD\".\n\n"
		f"User text:\n" + query
	)

	gemini_url = (
		f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
	)

	try:
		resp = requests.post(
			gemini_url,
			json={"contents": [{"parts": [{"text": prompt}]}]},
			timeout=30,
		)
		resp.raise_for_status()
		resp_json = resp.json()
		# The API returns the model text in candidates -> content -> parts -> text
		text = (
			resp_json.get("candidates", [{}])[0]
			.get("content", [{}])[0]
			.get("parts", [{}])[0]
			.get("text", "")
		)

		if not text:
			return _parse_booking_fallback(query)

		# Try to find a JSON object in the model output
		m = re.search(r"\{.*\}", text, re.S)
		if m:
			json_text = m.group(0)
			try:
				parsed = json.loads(json_text)
				# Ensure keys exist and default if not
				return {
					"name": parsed.get("name", "Unknown") if isinstance(parsed, dict) else "Unknown",
					"email": parsed.get("email", "Unknown") if isinstance(parsed, dict) else "Unknown",
					"date": parsed.get("date", "TBD") if isinstance(parsed, dict) else "TBD",
					"time": parsed.get("time", "TBD") if isinstance(parsed, dict) else "TBD",
				}
			except json.JSONDecodeError:
				# Fall through to fallback
				return _parse_booking_fallback(query)

		# If no JSON found, try to interpret the whole text as JSON
		try:
			parsed = json.loads(text)
			return {
				"name": parsed.get("name", "Unknown"),
				"email": parsed.get("email", "Unknown"),
				"date": parsed.get("date", "TBD"),
				"time": parsed.get("time", "TBD"),
			}
		except Exception:
			return _parse_booking_fallback(query)

	except Exception:
		# Any network/timeout or unexpected error -> use fallback
		return _parse_booking_fallback(query)

async def generate_response(query: str, session_id: str):
	vectorDBInstance = VectorDB(session_id)
	history = get_memory(session_id)

	# if any(keyword in query.lower() for keyword in ["book interview", "book a interview", "schedule interview", "schedule a interview", "interview", "book", "schedule"]):
	# 	booking_data = parse_booking(query)
	# 	try:
	# 		db = SessionLocal()
	# 		db.add(Booking(**booking_data))
	# 		db.commit()
	# 	except Exception:
	# 		# If DB write fails, still return confirmation to user but log/raise in real app
	# 		pass
	# 	return f"Interview booked for {booking_data['name']} on {booking_data['date']} at {booking_data['time']}"

	# Embed query locally with Ollama
	embedding = create_ollama_embedding([query])[0]

	# Retrieve context
	context_chunks = vectorDBInstance.search(embedding)
	# If vector_db returns objects, normalize to text; otherwise assume list[str]
	if context_chunks and isinstance(context_chunks[0], dict):
		context_text = "\n".join(c.get("text", "") for c in context_chunks)
	else:
		context_text = "\n".join(context_chunks or [])

	# Build prompt for Gemini
	full_prompt = f"""
        You are a helpful assistant.
        Context:
        {context_text}
        Conversation so far:
        {history}
        User: {query}
        Answer helpfully based on context.
        """

    
	gemini_url = (
		f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
	)
	print(full_prompt)
	resp = requests.post(
		gemini_url,
		json={"contents": [{"parts": [{"text": full_prompt}]}]},
		timeout=60,
	)
	resp.raise_for_status()
	resp_json = resp.json()
	print(resp_json)

	# def _extract_text_from_model_response(obj) -> str:
	# 	"""Robustly extract text from Gemini-like responses.

	# 	The Gemini API has varied response shapes across versions. This helper
	# 	attempts several common navigations and falls back safely to an empty
	# 	string when nothing sensible is found.
	# 	"""
	# 	if not obj:
	# 		return ""

	# 	# Common shape: {'candidates': [ { 'content': [ { 'parts': [ { 'text': '...' } ] } ] } ] }
	# 	try:
	# 		candidates = obj.get("candidates")
	# 		if isinstance(candidates, list) and candidates:
	# 			first = candidates[0]
	# 		elif isinstance(candidates, dict):
	# 			# sometimes candidates is a dict keyed by id
	# 			vals = list(candidates.values())
	# 			first = vals[0] if vals else candidates
	# 		else:
	# 			first = None

	# 		if isinstance(first, dict):
	# 			content = first.get("content")
	# 			if isinstance(content, list) and content:
	# 				part0 = content[0]
	# 			else:
	# 				part0 = first

	# 			if isinstance(part0, dict):
	# 				parts = part0.get("parts")
	# 				if isinstance(parts, list) and parts and isinstance(parts[0], dict):
	# 					return parts[0].get("text", "") or ""
	# 				# fallback to any text field on part0
	# 				if isinstance(part0.get("text"), str):
	# 					return part0.get("text", "")

	# 	except Exception:
	# 		# ignore and try other shapes
	# 		pass

	# 	# Other common shapes
	# 	for key in ("output", "outputs", "response", "text"):
	# 		val = obj.get(key)
	# 		if isinstance(val, str) and val:
	# 			return val
	# 		if isinstance(val, list) and val:
	# 			if isinstance(val[0], str):
	# 				return val[0]
	# 			if isinstance(val[0], dict):
	# 				return val[0].get("text", "") or ""

	# 	# Last resorts: try to stringify small dict fields
	# 	for k, v in obj.items():
	# 		if isinstance(v, str) and v:
	# 			return v

	# 	return ""

	# answer = _extract_text_from_model_response(resp_json)
	# if not answer:
	# 	# fallback to raw text body if model returned plain text
	# 	answer = resp.text or ""
	ans = resp_json.get("candidates", [{}])[0].get("content", [{}]).get("parts", [{}])[0].get("text", "")
	save_memory(session_id, query, ans)
	# # return answer
	return ans


