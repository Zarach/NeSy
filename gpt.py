import openai
import re

# Setzen Sie Ihren OpenAI API-Schlüssel
openai.api_key = "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"

# Definieren Sie eine Funktion, um Chat-GPT aufzurufen und eine Antwort zu erhalten
def ask_chat_gpt(prompt):
    response = openai.ChatCompletion.create(
        engine="gpt-3.5-turbo",  # Ersetzen Sie dies durch den genauen Namen des GPT-3.5-Modells
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Definieren Sie eine Funktion, um Problog-Code aus dem generierten Text zu extrahieren
def extract_problog_code(text):
    problog_code_pattern = re.compile(r'(?s)(?<=```problog).*?(?=```)', re.MULTILINE)
    problog_code = re.findall(problog_code_pattern, text)
    return "\n".join(problog_code)

# Beispiel: Erhalten Sie eine Antwort von Chat-GPT und extrahieren Sie den Problog-Code
start = "Prädikatenlogik innerhalb von ```problog``` Beschreibe in Prädikatenlogik: "

question = start+"Erstelle eine Regel für ein Säugetier 'schnabberlabber'. Ein Säugetier ist dann ein Säugetier, wenn es Fell hat und Eier legt."
response_text = ask_chat_gpt(question)
problog_code = extract_problog_code(response_text)

print(response_text)
print("Problog-Code:")
print(problog_code)