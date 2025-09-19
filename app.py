from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re

# Load environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("❌ GEMINI_API_KEY not found in .env file")

genai.configure(api_key=api_key)

app = Flask(__name__)

# ✅ Serve index.html at root
@app.route("/")
def home():
    return render_template("index.html")


# ✅ AI Listing Generation
@app.route("/generate-listing", methods=["POST"])
def generate_listing():
    try:
        data = request.json
        product_name = data.get("product_name", "")
        materials = data.get("materials", "")
        time_taken = data.get("time_taken", "")
        special_notes = data.get("special_notes", "")

        prompt = f"""
        Generate a JSON object with two fields: 'title' and 'description'.
        Write an attractive product title and a detailed description.
        Product: {product_name}
        Materials: {materials}
        Time Taken: {time_taken}
        Special Notes: {special_notes}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        raw_text = response.text.strip()
        print("Raw AI response:", raw_text)  # Debug log

        # Remove code fences if present
        clean_text = re.sub(r"^```(json)?", "", raw_text)
        clean_text = re.sub(r"```$", "", clean_text).strip()

        # Parse safely as JSON
        parsed = json.loads(clean_text)

        return jsonify(parsed)

    except Exception as e:
        print("Error during AI generation:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
