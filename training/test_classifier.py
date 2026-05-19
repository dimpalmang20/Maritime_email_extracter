import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from extraction.email_classifier import classify_email_type


sample_email = """

Cargo: 30,000 mts corn
LP: Paranagua
DP: Doha

"""


result = classify_email_type(sample_email)

print(result)