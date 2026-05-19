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

from extraction.orchestrator import orchestrate_extraction


sample_text = """
Cargo Corn from Paranagua to Doha
58000 DWT vessel
Laycan 16-20 July
"""


result = orchestrate_extraction(sample_text)

print(result)