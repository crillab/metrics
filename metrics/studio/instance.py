import abc
import json
import os
import shutil
import ssl
import urllib.request
from zipfile import ZipFile

import loguru
import pandas as pd
import requests
from alive_progress import alive_it

XCSP_URL = {
    "2017": ("https://www.cril.univ-artois.fr/~lecoutre/compets/instancesXCSP17.zip", "instancesXCSP17"),
    "2018": ("https://www.cril.univ-artois.fr/~lecoutre/compets/instancesXCSP18.zip", "instancesXCSP18"),
    "2019": ("https://www.cril.univ-artois.fr/~lecoutre/compets/instancesXCSP19.zip", "instancesXCSP19"),
    "2022": ("https://www.cril.univ-artois.fr/~lecoutre/compets/instancesXCSP22.zip", "instancesXCSP22"),
    "2023": ("https://www.cril.univ-artois.fr/~lecoutre/compets/instancesXCSP23.zip", "instancesXCSP23")
}


class Downloader(abc.ABC):
    def __init__(self, root_input_set):
        self._root_input_set = root_input_set

    @abc.abstractmethod
    def download(self,rename=None,list_of_files=None):
        pass


class InstanceDownloader(Downloader):
    def __init__(self, url, root_input_set="./input_set"):
        super().__init__(root_input_set)
        self._url = url

    def download(self, rename=None,list_of_files=None):
        # TODO
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = ssl._create_unverified_context
        loguru.logger.debug(self._url)
        r = requests.head(self._url, allow_redirects=True,verify=False)
        local_filename, headers = urllib.request.urlretrieve(r.url, filename=os.path.join(self._root_input_set,
                                                                                              r.url.split(os.path.sep)[-1]),)
        if local_filename.endswith(".zip"):
            with ZipFile(local_filename, "r") as z:
                root_dir = z.namelist()[0].split(os.path.sep)[0]
                z.extractall(path=self._root_input_set)
                if rename is not None:
                    os.rename(os.path.join(self._root_input_set, root_dir), os.path.join(self._root_input_set, rename))


class CompositeInstanceDownloader(Downloader):
    def __init__(self, file=None,base_url=None, root_input_set="./input_set"):
        super().__init__(root_input_set)
        self._file = file
        self._url = base_url

    def download(self,rename=None,list_of_files=None):
        urls = []
        if self._file is not None:
            with open(self._file, 'r') as f:
                urls = f.readlines()
        else:
            for f in list_of_files:
                urls.append(f"{self._url}/{f}")
        for item in alive_it(urls):
            downloader = InstanceDownloader(item, self._root_input_set)
            downloader.download()


class XCSPDownloader(Downloader):
    def __init__(self, year, root_input_set):
        super().__init__(root_input_set)
        self._year = year

    def download(self,rename=None,list_of_files=None):
        if self._year == -1:
            for key, t in alive_it(XCSP_URL.items()):
                url, name = t
                if not os.path.exists(os.path.join(self._root_input_set, name)):
                    InstanceDownloader(url, self._root_input_set).download(name)
        else:
            for y in alive_it(self._year):
                if not os.path.exists(os.path.join(self._root_input_set, "instancesXCSP" + str(y)[2:])):
                    InstanceDownloader(XCSP_URL[str(y)], self._root_input_set).download()


class XCSPFilter:
    def __init__(self, xcsp_cache, xcsp_metadata, arguments, root_input_set="./input_set"):
        self._filter_df = None
        self._xcsp_cache = xcsp_cache
        self._xcsp_metadata = xcsp_metadata
        self._root_input_set = root_input_set
        self._types = ['cop', 'csp', 'minicsp', 'minicop'] if arguments.get("types") == "all" else [
            arguments.get("types")]
        self._no_global_constraint = arguments.get("no_global_constraint")
        self._excluded = arguments.get("exclude") or []
        self._included = arguments.get("include") or []
        self._year = arguments.get("year")

    def filter(self) -> 'XCSPFilter':
        loguru.logger.info("Filtering XCSP instances...")

        dfs = []
        for t in self._types:
            for y in self._year:
                tmp = pd.read_json(os.path.join(self._xcsp_metadata, t + str(y)[2:] + ".json"))
                tmp["type"] = t
                dfs.append(tmp)
        df = pd.concat(dfs, ignore_index=True)

        all_global_constraint = set()

        for s in df["globalConstraints"]:
            for el in s:
                all_global_constraint.add(el["type"])

        for c in all_global_constraint:
            df[c] = df["globalConstraints"].apply(lambda x: next((el["count"] for el in x if el["type"] == c), 0))
        df["haveGlobalConstraint"] = df.apply(lambda x: any(x[c] > 0 for c in all_global_constraint), axis=1)
        self._filter_df = df.copy()

        query = []
        if self._no_global_constraint:
            query.append('haveGlobalConstraint')
        if len(self._types) > 0:
            query_types = ' | '.join([f'type=="{t}"' for t in self._types])
            query.append(query_types)
        if len(self._excluded) > 0:
            query_excluded = ' | '.join([f'{k}==0' for k in self._excluded])
            query.append(query_excluded)
        if len(self._included) > 0:
            query_include = ' | '.join([f'{k}>0' for k in self._included])
            query.append(query_include)
        loguru.logger.debug(query)
        if len(query) > 0:
            q = " & ".join([f"({r})" for r in query])
            loguru.logger.debug(q)
            self._filter_df = self._filter_df.query(q)
        loguru.logger.info(f"We select {self._filter_df['instance'].shape[0]} instances")
        return self

    def copy(self) -> None:
        loguru.logger.info("Copy selected instances to input_set directory...")
        for file in self._filter_df['instance'].values:
            shutil.copyfile(os.path.join(self._xcsp_cache, file),
                        os.path.join(self._root_input_set, file.split(os.path.sep)[-1]))

