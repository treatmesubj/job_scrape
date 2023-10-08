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
    page_num = 1
    while job_num < args.jobs:
        response_jobs = requests.get(
            f"https://builtin.com/jobs/remote&page={page_num}",
            cookies=cookiejar,
            allow_redirects=True,
        )

        soup = BeautifulSoup(response_jobs.text, "html.parser")

        job_post_elems = soup.select("[id^='job-card']")

        for elem in job_post_elems:
            company_name = elem.select_one("div[data-id] span").text
            job_title = elem.select_one("[href^='/job/']").text
            builtin_apply_url = (
                "https://builtin.com" + elem.select_one("[href^='/job/']")["href"]
            )

            response_builtin_job = requests.get(
                builtin_apply_url,
                cookies=cookiejar,
                allow_redirects=True,
            )

            soup = BeautifulSoup(response_builtin_job.text, "html.parser")
            job_apply_url = soup.select_one(
                "div[class*='apply-job-form'] div[data-path]"
            )["data-path"]

            post_csv = f'"{company_name}", "{job_title}", "{job_apply_url}"'
            print(f"[{job_num}]: {post_csv}")

            with open("./data/builtin-jobs.csv", "a") as f:
                f.write(f"{post_csv}\n")

            job_num += 1
        page_num += 1
