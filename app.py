
from flask import Flask, request, render_template_string
import os
import re

app = Flask(__name__)

def load_keywords(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip().lower() for line in f if line.strip())

red_flag_keywords = load_keywords("redflag.txt")
disease_keywords = load_keywords("diseases.txt")
symptom_keywords = load_keywords("symptoms.txt")

HTML_TEMPLATE = open("template.html", "r", encoding="utf-8").read()

# Words that can be used as a verb safely
safe_verb_context = {"aids", "supports", "helps", "promotes", "assists"}
prepositions = {"in", "with", "for", "to"}

@app.route("/", methods=["GET", "POST"])
def index():
    searched = ""
    result = ""
    is_compliant = True

    if request.method == "POST":
        claim = request.form.get("claim", "").strip().lower()
        searched = claim
        claim_words = set(re.findall(r"\b\w+\b", claim))

        red_flag_hit = red_flag_keywords & claim_words
        disease_hit = disease_keywords & claim_words
        symptom_hit = symptom_keywords & claim_words

        # Determine if safe context applies for red flag term (e.g., aids in, helps with)
        safe_usage_detected = False
        for word in safe_verb_context:
            if re.search(rf"\b{word}\b\s+(?:{'|'.join(prepositions)})\b", claim):
                if red_flag_hit == {word} and not (disease_hit or symptom_hit):
                    safe_usage_detected = True
                break

        if red_flag_hit or disease_hit or symptom_hit:
            if not safe_usage_detected:
                is_compliant = False
                result = "❌ Non-compliant: Claim appears to reference a drug-like benefit or symptom/disease."
            else:
                is_compliant = True
                result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."
        else:
            is_compliant = True
            result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."

    return render_template_string(HTML_TEMPLATE, searched=searched, result=result, is_compliant=is_compliant)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
