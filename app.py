
from flask import Flask, request, render_template_string

app = Flask(__name__)

with open("diseases.txt", "r", encoding="utf-8") as f:
    disease_keywords = [line.strip().lower() for line in f if line.strip()]
with open("symptoms.txt", "r", encoding="utf-8") as f:
    symptom_keywords = [line.strip().lower() for line in f if line.strip()]
with open("redflag.txt", "r", encoding="utf-8") as f:
    red_flag_keywords = [line.strip().lower() for line in f if line.strip()]

HTML_TEMPLATE = open("template.html", "r", encoding="utf-8").read()

@app.route("/", methods=["GET", "POST"])
def index():
    searched = ""
    result = ""
    is_compliant = True

    if request.method == "POST":
        claim = request.form.get("claim", "").lower().strip()
        searched = claim

        # Check against red flag, diseases, symptoms
        if any(word in claim for word in red_flag_keywords) or any(d in claim for d in disease_keywords) or any(s in claim for s in symptom_keywords):
            is_compliant = False
            result = "❌ Non-compliant: Claim appears to reference a drug-like benefit or symptom/disease."
        else:
            is_compliant = True
            result = "✅ Compliant: Claim appears to focus on general structure/function or wellness."

    return render_template_string(HTML_TEMPLATE, searched=searched, result=result, is_compliant=is_compliant)

if __name__ == "__main__":
    app.run(debug=True)
