
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

        # Separate out 'aids' usage if it's the only issue
        only_aids = (
            red_flag_hit == {"aids"} or disease_hit == {"aids"} or symptom_hit == {"aids"}
        ) and not (
            (red_flag_hit | disease_hit | symptom_hit) - {"aids"}
        )

        if only_aids:
            # Check if 'aids' is followed by valid structure/function language, not symptom/disease
            if re.search(r"\baids\b(?!\s+(?:in|with|for|to))\s+\b(?!pain|fracture|osteoporosis|arthritis|joint|diabetes)\w+\b", claim):
                is_compliant = True
                result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."
            else:
                is_compliant = False
                result = "❌ Non-compliant: Claim appears to reference a drug-like benefit or symptom/disease."
        elif red_flag_hit or disease_hit or symptom_hit:
            is_compliant = False
            result = "❌ Non-compliant: Claim appears to reference a drug-like benefit or symptom/disease."
        else:
            is_compliant = True
            result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."

    return render_template_string(HTML_TEMPLATE, searched=searched, result=result, is_compliant=is_compliant)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)
