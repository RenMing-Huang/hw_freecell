import os
from typing import List


def resolve_image_paths(raw_data_path: str, image_rels: List[str]) -> List[str]:
    """
    Resolve image relative paths to absolute paths without hard-coding any absolute base.
    Search order per image:
    1) As-is if absolute and exists
    2) Relative to the dataset file directory
    3) Relative to repository root (current working directory)
    4) Relative to Game-RL directory under repo root (for GameQA datasets)

    Only existing paths are returned; missing images are skipped.
    """
    if not image_rels:
        return []

    dataset_dir = os.path.abspath(os.path.dirname(raw_data_path)) if raw_data_path else os.getcwd()
    repo_root = os.getcwd()
    game_rl_dir = os.path.join(repo_root, "Game-RL")

    found = []
    for img_rel in image_rels:
        if not img_rel:
            continue
        # 1) Absolute existing
        if os.path.isabs(img_rel) and os.path.exists(img_rel):
            found.append(os.path.abspath(img_rel))
            continue
        # 2) Dataset dir
        candidate = os.path.join(dataset_dir, img_rel)
        if os.path.exists(candidate):
            found.append(os.path.abspath(candidate))
            continue
        # 3) Repo root
        candidate = os.path.join(repo_root, img_rel)
        if os.path.exists(candidate):
            found.append(os.path.abspath(candidate))
            continue
        # 4) Game-RL dir
        candidate = os.path.join(game_rl_dir, img_rel)
        if os.path.exists(candidate):
            found.append(os.path.abspath(candidate))
            continue
        # Not found: skip silently to avoid breaking evaluation
        # Optionally, could log here if a logger is desired
    return found
