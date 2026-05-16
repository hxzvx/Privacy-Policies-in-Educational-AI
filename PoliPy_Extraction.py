import polipy
import textstat

#url = "https://www.google.com/policies/privacy/"
url = "https://buddy.ai/en/privacy"
policy = polipy.get_policy(url)

# extract text (adjust key if needed)
text = policy.content['text']

# analyze
fk = textstat.flesch_kincaid_grade(text)
fe = textstat.flesch_reading_ease(text)

print(f"FK Grade: {fk}")
print(f"Reading Ease: {fe}")