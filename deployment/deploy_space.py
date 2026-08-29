"""
VariSetu — create and push the Gradio Space.

Run this locally, from the folder containing app.py, model_defs.py,
requirements.txt and README.md (i.e. the "space" folder). After
`huggingface-cli login`, this creates the Space (Gradio SDK, CPU-basic,
free) and uploads all four files in one shot.

USAGE:
    cd space/
    python ../upload_script/deploy_space.py
"""

from huggingface_hub import HfApi, create_repo

HF_USERNAME = "Saj2005"          # <-- change this
SPACE_ID = f"{HF_USERNAME}/VariSetu"

api = HfApi()

# create_repo(
#     repo_id=SPACE_ID,
#     repo_type="space",
#     space_sdk="gradio",
#     private=False,
#     exist_ok=True,
# )

api.upload_folder(
    folder_path=".",
    repo_id=SPACE_ID,
    repo_type="space",
    allow_patterns=["app.py", "model_defs.py", "requirements.txt", "README.md"],
)

print(f"Pushed. Space building at: https://huggingface.co/spaces/{SPACE_ID}")
print("First build takes a few minutes (installing torch/mediapipe/insightface). "
      "Watch progress in the Space's 'Logs' tab.")
