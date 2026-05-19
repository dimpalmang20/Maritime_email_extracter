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

from extraction.llm_fallback import send_to_llm


sample_email = """

Urgent vessel required.

Cargo: Coal
LP: Bushehr
DP: Doha
45000 mts
Laycan: 20-25 July

"""


result = send_to_llm(sample_email)

print(result)

