import os
from concurrent.futures import ThreadPoolExecutor
import datetime
from typing import List, Tuple
import typer
from chris.client import ChrisClient
from chris.models import UploadedFile
import logging
from pathlib import Path


def upload(client: ChrisClient, files: List[Path], parent_folder='', upload_threads=4):

    if parent_folder:
        upload_folder = f'{client.username}/uploads/{parent_folder}/{datetime.datetime.now().isoformat()}/'
    else:
        upload_folder = f'{client.username}/uploads/{datetime.datetime.now().isoformat()}/'

    input_files = []
    for mri in files:
        if mri.is_file():
            input_files.append(mri)
        elif mri.is_dir():
            if len(files) != 1:
                typer.secho(f'WARNING: contents of {mri} will be uploaded to the top-level, '
                            'i.e. directory structure is not preserved.', dim=True, err=True)
            input_files += [f.absolute().name for f in mri.rglob('*')]
        else:
            typer.secho(f'No such file or directory: {mri}', fg=typer.colors.RED, err=True)
            raise typer.Abort()

    with typer.progressbar(label='Uploading files', length=len(input_files)) as bar:
        def upload_file(input_file: str):
            client.upload(input_file, upload_folder)
            bar.update(1)

        with ThreadPoolExecutor(max_workers=upload_threads) as pool:
            uploads = pool.map(upload_file, input_files)

    # check for upload errors
    for upload_result in uploads:
        logging.debug(upload_result)

    typer.secho(f'Successfully uploaded {len(input_files)} files to "{upload_folder}"', fg=typer.colors.GREEN, err=True)
    return upload_folder


def download(client: ChrisClient, url: str, destination: Path, threads: 4):
    """
    Download all the files from a given ChRIS API url.
    :param client: ChRIS client
    :param url: any ChRIS file resource url, e.g.
                https://cube.chrisproject.org/api/v1/uploadedfiles/
                https://cube.chrisproject.org/api/v1/uploadedfiles/?fname=chris/uploads/today
                https://cube.chrisproject.org/api/v1/3/files/
    :param destination: folder on host where to download to
    :param threads: max number of concurrent downloads
    """
    if destination.is_file():
        typer.secho(f'Cannot download into {destination}: is a file', fg=typer.colors.RED, err=True)
        raise typer.Abort()

    def __calculate_target(remote_file: UploadedFile) -> Tuple[Path, UploadedFile]:
        """
        Decide on a download location for a file resource in ChRIS.
        Create the parent directory if needed.
        :param remote_file: file information from ChRIS
        :return: download location on host and that file
        """
        fname = remote_file.fname
        if fname.startswith('chris/'):
            fname = fname[6:]
        target = destination.joinpath(fname)
        os.makedirs(target.parent, exist_ok=True)
        return target, remote_file

    search = client.get_uploadedfiles(url)
    with typer.progressbar(search, length=len(search), label='Getting information') as progress:
        to_download = frozenset(__calculate_target(remote_file) for remote_file in progress)

    with typer.progressbar(length=len(to_download), label='Downloading files') as progress:
        def download_file(t: Tuple[Path, UploadedFile]) -> int:
            """
            Download file and move the progress bar
            :param t: tuple
            :return: downloaded file size
            """
            target, remote_file = t
            remote_file.download(target)
            progress.update(1)
            return target.stat().st_size

        with ThreadPoolExecutor(max_workers=threads) as pool:
            sizes = pool.map(download_file, to_download)

    total_size = sum(sizes)
    if total_size < 2e5:
        size = f'{total_size} bytes'
    elif total_size < 2e8:
        size = f'{total_size / 1e6:.4f} MB'
    else:
        size = f'{total_size / 1e9:.4f} GB'
    typer.secho(size, fg=typer.colors.GREEN, err=True)
