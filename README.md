# Freshness Crawler

## Introduction

Freshness crawler is a generic web crawler that receives a list of input URLs and crawl them as many levels deep as needed.

## Objective

- Build web graphs generated by given seeds;
- Schedule a crontab task for daily crawl, in order to build a static dataset of these graphs;
- Analyze the behavior of these pages, in order to find patterns in how new links appear on the web;
- The hypothesis is that the dataset will enable a machine learning algorithm to predict the likelihood of a page having new links that pertain to a given topic;

## Run Crawler

  `python src/crawler.py <seed_file> <depth_of_crawl>`

## Google Docs

 https://docs.google.com/document/d/1fr5l-gL2UA66BlAqblK-kBgb0mnPQzcTMRVvTxKn_Qs/edit