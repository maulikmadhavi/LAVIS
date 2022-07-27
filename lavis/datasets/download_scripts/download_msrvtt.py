import os
from pathlib import Path

from omegaconf import OmegaConf

from lavis.common.utils import (
    cleanup_dir,
    download_and_extract_archive,
    get_abs_path,
    get_cache_path,
)


DATA_URL = {
    "train": "https://download1079.mediafire.com/wohbpb72pvsg/x3rrbe4hwp04e6w/train_val_videos.zip",
    "test": "https://download2390.mediafire.com/qci0911s7sgg/czh8sezbo9s4692/test_videos.zip",
}


def download_datasets(root, url):
    """
    Download the Imagenet-R dataset archives and expand them
    in the folder provided as parameter
    """
    download_and_extract_archive(url=url, download_root=root)


def merge_datasets(download_path, storage_path):
    """
    Merge datasets in download_path to storage_path
    """

    # Merge train and test datasets
    train_path = os.path.join(download_path, "TrainValVideo")
    test_path = os.path.join(download_path, "TestVideo")
    train_test_path = storage_path

    print("Merging to {}".format(train_test_path))

    os.makedirs(train_test_path, exist_ok=True)

    for file_name in os.listdir(train_path):
        os.rename(
            os.path.join(train_path, file_name),
            os.path.join(train_test_path, file_name),
        )

    for file_name in os.listdir(test_path):
        os.rename(
            os.path.join(test_path, file_name),
            os.path.join(train_test_path, file_name),
        )


if __name__ == "__main__":

    config_path = get_abs_path("configs/datasets/msrvtt/defaults_cap.yaml")

    storage_dir = OmegaConf.load(
        config_path
    ).datasets.msrvtt_cap.build_info.videos.storage

    download_dir = Path(get_cache_path(storage_dir)).parent / "download"
    storage_dir = Path(get_cache_path(storage_dir))

    if storage_dir.exists():
        # ask users to confirm
        ans = input(
            "{} exists. Do you want to delete it and re-download? [y/N] ".format(
                storage_dir
            )
        )

        if ans in ["y", "Y", "yes", "Yes"]:
            cleanup_dir(storage_dir)
            cleanup_dir(download_dir)
            os.makedirs(download_dir)
        else:
            print("Aborting")
            exit(0)

    try:
        for k, v in DATA_URL.items():
            print("Downloading {} to {}".format(v, k))
            download_datasets(download_dir, v)
    except Exception as e:
        # remove download dir if failed
        cleanup_dir(download_dir)
        print("Failed to download or extracting datasets. Aborting.")

    try:
        merge_datasets(download_dir, storage_dir)
    except Exception as e:
        # remove storage dir if failed
        cleanup_dir(download_dir)
        cleanup_dir(storage_dir)
        print("Failed to merging datasets. Aborting.")

    cleanup_dir(download_dir)
