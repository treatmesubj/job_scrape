#!/usr/bin/env python3
import os
import json
import requests
from bs4 import BeautifulSoup
import browser_cookie3
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jobs",
        "-j",
        action="store",
        type=int,
        default=20,
        help="int, number of jobs to scrape",
    )
    args = parser.parse_args()

    # cookiejar = browser_cookie3.load()  # all browsers
    cookiejar = browser_cookie3.firefox()

    job_num = 0
    while job_num < args.jobs:
        response_jobs = requests.get(
            f"https://www.linkedin.com/jobs/search/?keywords=&location=United States&f_TPR=&f_WT=2&start={job_num}",
            cookies=cookiejar,
            allow_redirects=True,
        )

        soup = BeautifulSoup(response_jobs.text, "html.parser")

        jobs_elem = soup.select("[id^='bpr-guid']")[-1]

        sanjay = json.loads(jobs_elem.text)
        job_keys = [
            key
            for key in sanjay["data"]["metadata"]["jobCardPrefetchQueries"][0][
                "prefetchJobPostingCard"
            ].keys()
        ]
        job_ids = [key.split("(")[-1].split(",")[0] for key in job_keys]
        # print(f"{job_ids=}")

        for id in job_ids:
            job_id_url = f"https://www.linkedin.com/jobs/search/?currentJobId={id}"
            response_job = requests.get(
                job_id_url,
                cookies=cookiejar,
                allow_redirects=True,
            )

            soup = BeautifulSoup(response_job.text, "html.parser")
            job_post_elems = soup.select("[id^='bpr-guid']")

            for elem in job_post_elems:
                try:
                    sanjay = json.loads(elem.text)
                    job_apply_method = sanjay["data"]["applyMethod"]
                    break
                except KeyError:
                    pass
            else:
                raise Exception(f"{id} job is weird")

            if "companyApplyUrl" in job_apply_method.keys():
                job_apply_url = job_apply_method["companyApplyUrl"]  # company site
            elif "easyApplyUrl" in job_apply_method.keys():  # LinkedIn Easy-Apply
                job_apply_url = job_id_url
            elif (
                "SimpleOnsiteApply" in job_apply_method["$type"]
            ):  # LinkedIn super Easy-Apply
                job_apply_url = job_id_url
            else:
                raise Exception(f"{job_id_url}, no apply URL?")

            job_title = sanjay["data"]["title"]
            company_name = sanjay["included"][1]["name"]

            post_csv = f'"{company_name}", "{job_title}", "{job_apply_url}"'
            print(f"[{job_num}]: {post_csv}")

            with open("./data/linkedin-jobs.csv", "a") as f:
                f.write(f"{post_csv}\n")

            job_num += 1