"""
VariSetu — upload trained weights to Hugging Face Model repos.

Run this ONCE locally (where your three .pt files already live) after
`huggingface-cli login`. It creates three separate Model repos and uploads
each model's weight file + model_config.json to its own repo. Keeping
weights in dedicated Model repos (rather than inside the Space repo) is
the standard pattern — the Space then pulls them at startup with
hf_hub_download(), and you can update a model later without touching the
Space's app code.

USAGE:
    pip install huggingface_hub
    huggingface-cli login          # if you haven't already
    python upload_weights.py

Fill in HF_USERNAME and the four local file paths below, then run it.
Large files (a few hundred MB, which is typical for these three models)
upload fine on the free tier — huggingface_hub handles chunking/resume
automatically.
"""

from huggingface_hub import HfApi, create_repo

# ---------------------------------------------------------------------------
# EDIT THESE
# ---------------------------------------------------------------------------
HF_USERNAME = "Saj2005"          # <-- change this

LOCAL_PATHS = {
    "crowd_density": {
        "weights": "Model1_CrowdDensity/crowd_density_model.pt",     # <-- change
        "config":  "Model1_CrowdDensity/model_config.json",    # <-- change
        "repo_id": f"{HF_USERNAME}/varisetu-crowd-density",
    },
    "fall_detection": {
        "weights": "Model2_Fall_Detection/fall_model.pt",               # <-- change
        "config":  "Model2_Fall_Detection/model_config.json",      # <-- change
        "repo_id": f"{HF_USERNAME}/varisetu-fall-detection",
    },
    "person_reid": {
        "weights": "Model3_Person_Reidentification/reid_model.pt",                # <-- change
        "config":  "Model3_Person_Reidentification/Model 3 Artifacts/model_config.json",       # <-- change
        "repo_id": f"{HF_USERNAME}/varisetu-person-reid",
    },
}
# ---------------------------------------------------------------------------

api = HfApi()

for name, info in LOCAL_PATHS.items():
    print(f"\n=== {name} -> {info['repo_id']} ===")

    # Creates the repo if it doesn't exist yet; no-ops if it already does.
    create_repo(repo_id=info["repo_id"], repo_type="model", private=False, exist_ok=True)

    print("Uploading weights (this is the big file, may take a while)...")
    api.upload_file(
        path_or_fileobj=info["weights"],
        path_in_repo=info["weights"].split("/")[-1],
        repo_id=info["repo_id"],
        repo_type="model",
    )

    print("Uploading model_config.json...")
    api.upload_file(
        path_or_fileobj=info["config"],
        path_in_repo="model_config.json",
        repo_id=info["repo_id"],
        repo_type="model",
    )

    print(f"Done: https://huggingface.co/{info['repo_id']}")

print("\nAll uploads complete.")
